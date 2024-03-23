from datetime import datetime

from src.common.logger import logger


def update_last_runtime() -> None:
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info("Updating last run time")
    with open("last_runtime.txt", "w") as f:
        f.write(time)
