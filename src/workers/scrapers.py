from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import (
    presence_of_element_located
)
from datetime import datetime
from time import sleep
from workers.writers import index_es, write_csv
import logging


def el_locate(browser, timeout, log_directory, element):
    ''' This function wraps Selenium locators by putting all locating
    tasks under wait. Waiting for elements serves as a safety-net for
    the program's logic.

    Take:
    3 parameters: browser, element
    - browser: a session of Selenium WebDriver
    - element: a tuple in the format of (method, value)
    - timeout: timeout second

    Return: 1 locator object
    '''

    try:
        locator = WebDriverWait(browser, timeout).until(
            presence_of_element_located((element[0], element[1]))
        )
    except:
        now = datetime.now().strftime("%Y%m%d-%H%M%S")
        screenshot = log_directory + now
        browser.save_screenshot(screenshot)
        logging.info("Failed to locate Element: " + element[1])
        logging.info("Browser screenshot is saved at: " + screenshot)
    else:
        logging.info("Element located: " + element[1])
        return locator


def fetch_body(browser, conf, url):
    ''' This function fetches a web page's content.

    Take:
    3 parameters: browser, url, elements
    - browser: a session of Selenium WebDriver
    - url: an url string
    - elements: a dict contains of locators of the web page's
                finishing HTML/CSS elements, in the format of
                { "content_loaded" : [ method, value ],
                  "body" : [ method, value ] }

    Return: 1 locator object

    Notes: For some reasons, the page isn't fully loaded in PhantomJS
    after "chartcontrolheader" shown up. Seems to be another specific
    issue of PhantomJS. There is a hotfix implemented for now.
    '''

    browser.get("about:blank")
    browser.get(url)

    timeout = conf.get("timeout")
    log_dir = conf.get("log_dir")

    el_locate(browser, timeout, log_dir, conf.get("el_content_loaded"))

    # Wait for graceful interval after "chartcontrolheader" is loaded as
    # a **safety net**. graceful is merely a figure of my experience.
    # TODO: Need to know WHY. This is a hotfix
    sleep(conf.get("graceful"))

    locator = el_locate(browser, timeout, log_dir, conf.get("el_body"))

    return locator


def parse_body(body, country, field_keys):
    ''' This function cut a web page's body to get needed data.

    Take:
    1 parameter: body
    - body: a web page's HTML body

    Return: 1 list of parsed items

    Notes: This funtions will fail when body is broken or missing.
    It's a known problem that needs a fix later on.
    '''
    try:
        s1 = body.split("Date\nInstallations\n")[1]

    except IndexError as e:
        logging.info(e)
        raise

    else:
        s2 = s1.split("Copyright")[0]

        data = []

        evens = s2.splitlines()[0:][::2]
        odds = s2.splitlines()[1:][::2]

        for i, timestamp in enumerate(evens):
            values = [timestamp, country, odds[i]]
            entry = dict(zip(field_keys, values))
            data.append(entry)

        logging.info(data)

        return data


def process_data(browser, conf, urls_di):

    for i, data in enumerate(urls_di):

        countrycode = urls_di[i]["country_code"]
        country = conf.get("inv_cc")[countrycode]
        timestamp = urls_di[i]["timestamp_month"]
        url_di = data["url_di"]

        body = fetch_body(browser, conf, url_di)
        try:
            raw_data = parse_body(body.text, country,
                                  conf.get("record_keys_di"))
        except IndexError as e:
            logging.info(body.text)
            logging.info("Failed to crawl for data. "
                         "Skipping index_es and write_csv")
        else:
            index_es(conf, conf.get("dw_conn"), conf.get("record"),
                     reversed(raw_data), country)

            write_csv(conf, country,
                      reversed(raw_data), timestamp)

        sleep(conf.get("graceful"))
