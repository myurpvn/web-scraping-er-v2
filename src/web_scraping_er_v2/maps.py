from requests import get
import pandas as pd
import json
import yaml
import os

from src.common.logger import logger


cc_map_dir = "maps/currency_country_map.yaml"
sub_map_dir = "maps/subscription_map.yaml"


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
    with open(cc_map_dir, "r") as file:
        return yaml.safe_load(file)


def write_cc_map(
    data: dict[str, dict], currency_code: str, country_list: list[str]
) -> None:
    data[currency_code] = {"countries": list(set(country_list))}
    with open(cc_map_dir, "w") as file:
        yaml.dump(data, file)


def read_sub_map() -> list[str]:
    with open(sub_map_dir, "r") as file:
        return yaml.safe_load(file)["subscription_list"]


def update_sub_map(currency_code: str) -> None:
    data = read_sub_map()
    sub_list = data["subscription_list"]
    sub_list.append(currency_code)
    data = {"subscription_list": list(set(sub_list))}
    with open(sub_map_dir, "w") as file:
        yaml.dump(data, file)


def get_cc_map_country_list(
    currency_code: str, is_updated: bool
) -> tuple[list[str], bool]:
    country_list = None
    currency_code_map: dict = {}

    if currency_code == "VEF":  # bug on x-rates site for VENEZUELAN BOLIVAR
        currency_code = "VES"

    if os.path.exists(cc_map_dir):
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
