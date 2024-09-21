import os, logging, sys

from requests_html import HTMLSession

# Project internal imports
from utils import utils
from scraper_topics import save_all_topics_words
from scraper_opal import save_all_opal_words
from config import CONFIG_SCRAPED_DATA_DIR
from logger import customLog


def main():
    logging.setLoggerClass(customLog)
    log = customLog(__name__)

    if not utils.check_internet_connection():
        log.critical("No internet. Exiting")
        sys.exit(1)

    session = HTMLSession()

    os.makedirs(CONFIG_SCRAPED_DATA_DIR, exist_ok=True)
    log.done("Created [Scraped Data] folder")

    did_got_opal = save_all_opal_words(session)
    did_got_topics = save_all_topics_words(session)

    session.close()

    if did_got_opal and did_got_topics:
        log.done("Success. All scraped!")


if __name__ == "__main__":
    main()
