import os, sys, logging, time

from requests.exceptions import RequestException
from bs4 import BeautifulSoup

# Project internal imports
from utils import utils
from logger import customLog
from config import CONFIG_RENDER_JS, CONFIG_SCRAPED_DATA_DIR

OPAL_URL = 'https://www.oxfordlearnersdictionaries.com/wordlistsopal'
logging.setLoggerClass(customLog)
log = customLog(__name__)

def save_all_opal_words(session):

    data_folder = os.path.join(CONFIG_SCRAPED_DATA_DIR, 'Opal')
    os.makedirs(data_folder, exist_ok=True)
    log.done('Created Opal folder')

    log.job_running('Getting Opal page HTML')
    try:
        response = utils.fetch_page(session, OPAL_URL)
    except RequestException:
        if not utils.check_internet_connection():
            log.critical('Exiting. Try later')
            sys.exit(1)
        
        log.critical('Couldn\'t get Opal page HTML. Opal won\'t be scraped')
        return 

    log.done('Got Opal page HTML')
    
    if CONFIG_RENDER_JS:
        log.debug('Rendering JS')
        response.html.render()

    soup = BeautifulSoup(response.content, 'html.parser')
    css_selector = '#wordlistsContentPanel > .top-g > [data-opal_written] > a'
    words = sorted(set(word.text.strip() for word in soup.select(css_selector)))

    if not words:
        log.critical('Couldn\'t extract any words. Proceding without Opal')
        return

    filepath = os.path.join(data_folder, 'Words.txt')
    with open(filepath, 'w') as file:
        file.write("\n".join(words))
    log.done('Saved Opal words to a file')

    return 1
