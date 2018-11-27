import logging
import time

from bot.discount_finder import scheduled_job
from bot.config import Config
from bot.poster import Poster


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
    level=Config.log_level
)

poster = Poster()

while True:
    try:
        scheduled_job(poster)
    except Exception:
        logging.exception(
            """\n
            ################ EXCEPTION ################\n
            Scheduled job ended with uncaught exception\n
            """
        )
    time.sleep(Config.job_interval_sec)
