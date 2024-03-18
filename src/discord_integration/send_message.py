from requests import post, Response
import pandas as pd
import os
import json

WEBHOOK = os.getenv("DISCORD_WEBHOOK")


class WebhookRequest:
    pass


TEMPLATE = {
    "content": "",
    "embeds": [],
}


def post_message(payload: str) -> Response:
    try:
        response = post(
            WEBHOOK, json.dumps(payload), headers={"Content-type": "application/json"}
        )
        if not str(response.status_code).startswith("2"):
            raise Exception(
                f"response status: {response.status_code}, error: {response.text}"
            )
        return response
    except Exception as e:
        raise Exception(e)


def send_simple_text(message: str) -> None:
    payload = TEMPLATE
    payload["content"] = message
    response = post_message(payload)


def send_dataframe(df: pd.DataFrame) -> None:
    fields = []
    base = df["home_currency"].iloc[0]

    for row in df.values:
        if len(fields) >= 20:
            break
        currency = {"name": "Currency", "value": str(row[1])}
        value = {"name": f"Value ({base})", "value": str(row[3]), "inline": True}
        fields.append(currency)
        fields.append(value)

    payload = TEMPLATE
    payload["embeds"] = [{"fields": fields}]
    response = post_message(payload)


def send_dataframe_as_text(df: pd.DataFrame) -> None:
    base = df["home_currency"].iloc[0]
    content = ""
    for row in df.values:
        if len(content) >= 1999:
            break
        else:
            content += f"1 {row[1]} => {round(row[3], 3)} {base}\n"

    payload = TEMPLATE
    payload["content"] = content
    response = post_message(json.dumps)
