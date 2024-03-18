from requests import get
import pandas as pd
import json
import yaml
import os

from src.common.logger import logger


def update_cc_map(currency_code_map: dict[str, dict], currency_code: str) -> list[str]:
    url = f"https://restcountries.com/v3.1/currency/{currency_code}?fields=name"
    try:
        response = get(url)
        country_list = [c["name"]["common"] for c in json.loads(response.text)]
        write_cc_map(currency_code_map, currency_code, country_list)
        return country_list
    except Exception as e:
        raise e


def read_cc_map() -> dict[str, dict]:
    with open("currency_country_map.yaml", "r") as file:
        return yaml.safe_load(file)


def write_cc_map(
    data: dict[str, dict], currency_code: str, country_list: list[str]
) -> None:
    data[currency_code] = {"countries": list(set(country_list))}
    with open("currency_country_map.yaml", "w") as file:
        yaml.dump(data, file)


def get_cc_map_country_list(
    currency_code: str, is_updated: bool
) -> tuple[list[str], bool]:
    country_list = None
    currency_code_map: dict = {}

    if currency_code == "VEF":  # bug on x-rates site for VENEZUELAN BOLIVAR
        currency_code = "VES"

    if os.path.exists("currency_country_map.yaml"):
        currency_code_map = read_cc_map()
        if currency_code in currency_code_map.keys():
            country_list = currency_code_map[currency_code]["countries"]

    if country_list is None:
        logger.info("Updating map", currency_code=currency_code)
        country_list = update_cc_map(currency_code_map, currency_code)
        is_updated = True

    return [country_list, is_updated]


def generate_cc_map_df() -> pd.DataFrame:
    cc_map = read_cc_map()
    cc_map_df = pd.DataFrame(data=cc_map.values(), index=cc_map.keys())
    cc_map_df["currency"] = cc_map_df.index
    cc_map_df = cc_map_df.explode(["countries"])
    return cc_map_df
