from datetime import datetime, timedelta
from secrets import token_hex

from loguru import logger

logger.remove()

logger.add(
    f"logs/{datetime.today().strftime('%d-%m-%Y')}/{token_hex(10)}.log",
    format="{level}:{time:DD-MM-YYYY:HH:mm:ss}:{file.name}:{function}:{line} - {message} {extra}",
    retention=timedelta(days=7),
)
