from google.cloud import bigquery
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz
import pandas as pd
import base64
import json
import os


tz = pytz.timezone("Asia/Colombo")
dataset = "exchange_rates"


def init_bq_connection() -> tuple[Credentials, bigquery.Client]:
    json_acct_info = json.loads(base64.b64decode(os.getenv("GOOGLE_CREDENTIALS_B64")))
    credentials = Credentials.from_service_account_info(
        json_acct_info,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    client = bigquery.Client(
        credentials=credentials,
        project=credentials.project_id,
    )
    return [credentials, client]


def bq_load_daily(df: pd.DataFrame, base_currency: str) -> dict[str, str]:
    load_time = datetime.now(tz)
    credentials, client = init_bq_connection()
    df["date"] = load_time.strftime("%Y-%m-%d")
    df["time"] = load_time.strftime("%H:%M:%S")
    df["bq_load_time"] = load_time
    result = {"status": "", "error": "N/A"}
    try:
        table = f"{credentials.project_id}.{dataset}.daily_exchange_rate_base_{base_currency}"

        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            schema_update_options=bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION,
        )
        job = client.load_table_from_dataframe(df, table, job_config=job_config)
        job.result()
        table = client.get_table(table)
    except Exception as e:
        result["status"] = "FAILED"
        result["error"] = str(e)
    else:
        result["status"] = "SUCCESS"

    return result


def bq_load_map(df: pd.DataFrame) -> dict[str, str]:
    credentials, client = init_bq_connection()
    result = {"status": "", "error": "N/A"}
    try:
        table = f"{credentials.project_id}.{dataset}.currency_country_map"
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )
        job = client.load_table_from_dataframe(df, table, job_config=job_config)
        job.result()
        table = client.get_table(table)
    except Exception as e:
        result["status"] = "FAILED"
        result["error"] = e
    else:
        result["status"] = "SUCCESS"

    return result
