import requests, logging, time
from functools import wraps
from requests.exceptions import RequestException

# Project internal imports
from logger import customLog
from config import CONFIG_MAX_RETRIES, CONFIG_RETRY_DELAY

logging.setLoggerClass(customLog)
log = customLog(__name__)


def retry_fetching(
    attempts=CONFIG_MAX_RETRIES, delay=CONFIG_RETRY_DELAY, exceptions=(Exception,)
):
    """
    Decorator to retry a function if it raises specified exceptions.

    :param attempts: Number of retry attempts.
    :param delay: Delay between attempts in seconds.
    :param exceptions: Tuple of exception types to catch and retry.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    log.warning(
                        f"Attempt {attempt} failed. {attempts - attempt} more to try"
                    )
                    log.debug(f"Exception -- {e}")
                    if attempt < attempts:
                        time.sleep(delay)
                    else:
                        raise

        return wrapper

    return decorator


class utils:
    @staticmethod
    def check_internet_connection(url="http://www.google.com"):
        log.debug("Checking internet connection")
        try:
            response = requests.get(url, timeout=5)
            log.debug("OK > internet connection")
            return response.status_code == 200
        except requests.ConnectionError:
            log.debug("No internet connection")
            return False

    @staticmethod
    def sanitize_filename(name):
        REPLACE_WITH = "_"
        CHARS_TO_REPLACE = ["/", "\\", ":", "*", "?", '"', ">", "<", "|"]

        for char in CHARS_TO_REPLACE:
            name = name.replace(char, REPLACE_WITH)

        return name

    @staticmethod
    @retry_fetching(exceptions=(RequestException,))
    def fetch_page(session, url):
        log.debug(f"Getting {url}")
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return response
