from datetime import datetime
import pytz

from src.common.logger import logger

tz = pytz.timezone("Asia/Colombo")


def update_last_runtime() -> None:
    time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    logger.info("Updating last run time")
    with open("last_runtime.txt", "w") as f:
        f.write(time)
