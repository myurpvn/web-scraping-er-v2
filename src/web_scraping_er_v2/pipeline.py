from requests import get
from bs4 import BeautifulSoup
import pandas as pd

from web_scraping_er_v2.maps import get_cc_map_country_list, generate_cc_map_df, read_sub_map
from src.web_scraping_er_v2.load_to_bq import bq_load_daily, bq_load_map
from src.discord_integration.send_message import send_simple_text, send_dataframe_as_text
from src.common.logger import logger

def pipeline(base_currency):
    logger.info("Staring script", base_currency=base_currency)
    
    logger.info("Getting website data")
    exchange_rate_map = {}
    response = get(f"https://www.x-rates.com/table/?from={base_currency}&amount=1")
    
    logger.info("Extracting data from website")
    is_updated = False
    soup = BeautifulSoup(response.content, "html.parser")
    for row in soup.find_all("td", class_="rtRates"):
        row = str(row)
        if f";to={base_currency}" in row:
            extracted = str(row[row.find("/?") + 2 : row.find("</a")])
            cleaned = (
                extracted.replace("from=", "")
                .replace("to=", "")
                .replace("&amp;", ";")
                .replace('">', ";")
            )
            for_curr, home_curr, curr_value = cleaned.split(";")
            country_list, is_updated = get_cc_map_country_list(for_curr, is_updated)
            exchange_rate_map[for_curr] = {
                "countries": country_list,
                "foreign_currency": for_curr,
                "home_currency": home_curr,
                "value": float(curr_value),
            }

    logger.info("Building DataFrame")
    exchange_rates_df = pd.DataFrame(
        data=exchange_rate_map.values(), index=exchange_rate_map.keys()
    )

    # exchange_rates_df.to_csv("sample_rates.csv", index=False)
    logger.info("Running Daily refresh")
    result = bq_load_daily(exchange_rates_df, base_currency)
    if result["status"] == "FAILED":
        logger.info("BQ Load Failed", exception=result["error"])
        send_simple_text(f"BQ Daily run Failed,  error: {result["error"]}")
    else:
        # checking and sending subscribed exchange-rates
        sub_list = read_sub_map()
        logger.info("Sending ex-rates", subscribed=sub_list)
        discord_df = exchange_rates_df[exchange_rates_df["foreign_currency"].isin(sub_list)]
        send_dataframe_as_text(discord_df)

    if is_updated:
        map_cc_df = generate_cc_map_df()
        logger.info("Updating Map table")
        result = bq_load_map(map_cc_df)
        # logger.info("Sending result to Discord", row_count=len(map_cc_df))
        # send_simple_text(f"BQ Map Data Loading: {result["status"]}, error: {result["error"]}")
