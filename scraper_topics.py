import os, sys, logging

from bs4 import BeautifulSoup
from requests.exceptions import RequestException

# Project internal imports
from config import CONFIG_RENDER_JS, CONFIG_SCRAPED_DATA_DIR
from utils import utils
from logger import customLog

TOPICS_URL = "https://www.oxfordlearnersdictionaries.com/topic/"
logging.setLoggerClass(customLog)
log = customLog(__name__)


def save_all_topics_words(session):
    data_folder = os.path.join(CONFIG_SCRAPED_DATA_DIR, "Topics")
    os.makedirs(data_folder, exist_ok=True)
    log.done("Created [Topics] Folder")

    topics = scrape_topics(session)
    if not topics:
        log.critical("Couldn't scrape topics.")
        return

    for topic_name, topic_url in topics.items():
        topic_dir_name = os.path.join(data_folder, topic_name)
        os.makedirs(topic_dir_name, exist_ok=True)
        log.done(f"Created {topic_name} folder")

        subtopics = scrape_subtopics(session, topic_url)
        for subtopic_name, sub_subtopics in subtopics.items():
            subtopic_dir_name = os.path.join(topic_dir_name, subtopic_name)
            os.makedirs(subtopic_dir_name, exist_ok=True)
            log.done(f"Created {subtopic_name} subtopic of {topic_name} folder")

            for sub_subtopic_name, sub_subtopic_url in sub_subtopics.items():
                words = scrape_words(session, sub_subtopic_url)
                filename = sub_subtopic_name + ".txt"
                filepath = os.path.join(subtopic_dir_name, filename)
                with open(filepath, "w") as file:
                    file.write("\n".join(words))
                log.done(f"Saved all words to {filename}")

    return 1


def scrape_topics(session):
    log.job_running("Scraping topics")

    try:
        log.debug(f"Getting {TOPICS_URL}")
        response = utils.fetch_page(session, TOPICS_URL)
    except RequestException:
        if not utils.check_internet_connection():
            log.critical("No internet. Exiting")
            sys.exit(1)

        log.critical("Couldn't get Topics page HTML. Topics won't be saved")
        return

    log.debug("Got Topics page HTML")

    if CONFIG_RENDER_JS:
        log.debug("Rendering JS")
        response.html.render()

    soup = BeautifulSoup(response.content, "html.parser")
    topic_boxes = soup.select(".topic-box")

    topics = {}
    for topic in topic_boxes:
        name = topic.select_one(".topic-label")
        link = topic.select_one("a")
        name_text = utils.sanitize_filename(name.get_text(strip=True))
        href = link.get("href")
        topics[name_text] = href

    return topics


def scrape_subtopics(session, url):
    try:
        log.debug(f"Getting {url}")
        response = utils.fetch_page(session, url)
        log.debug("Got Subtopics page HTML")

        if CONFIG_RENDER_JS:
            log.debug("Rendering JS")
            response.html.render()

        soup = BeautifulSoup(response.content, "html.parser")
        subtopic_boxes = soup.select(".topic-box.topic-box-secondary")

        subtopics = {}
        for subtopic in subtopic_boxes:
            sub_subtopic_atag = subtopic.select_one("a")
            sub_subtopic_text = sub_subtopic_atag.get_text(strip=True)
            sub_subtopic_name = utils.sanitize_filename(
                sub_subtopic_text[: -len("(see all)")]
            )

            subtopics[sub_subtopic_name] = {}

            l3_elements = subtopic.select_one(".l3")
            links = l3_elements.find_all("a")

            for link in links:
                name = utils.sanitize_filename(link.get_text(strip=True))
                href = link.get("href")
                subtopics[sub_subtopic_name].update({name: href})

        return subtopics

    except RequestException as e:
        log.debug(f"Error: {e}")
        return {}


def scrape_words(session, url):
    try:
        log.debug(f"Getting {url}")
        response = utils.fetch_page(session, url)
        log.debug("Got words page HTML")

        if CONFIG_RENDER_JS:
            log.debug("Rendering JS")
            response.html.render()

        soup = BeautifulSoup(response.content, "html.parser")
        div = soup.find("div", id="wordlistsContentPanel")
        attribute = "data-" + url.split("sublist=")[-1]
        list_items = div.find_all("li", attrs={attribute: True})

        words = []
        for item in list_items:
            link = item.find("a")
            if link:
                text = link.get_text()
                words.append(text)

        return words

    except RequestException as e:
        log.debug(f"Error: {e}")
        return []
