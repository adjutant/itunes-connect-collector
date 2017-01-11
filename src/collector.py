#!/usr/bin/env python
# coding=utf8


from time import sleep
import logging
from workers.session import argparser, session_init, daemonize
from workers.login import login
from workers.scrapers import process_data
from modules.logger import logger


def worker(opts):

    browser, conf = session_init(opts)

    logger(conf.get("log_file"))
    logging.info("Started a crawling run")

    try:
        login(browser, conf)
    except:
        logging.info("Failed to login, skipping this run")
    else:
        urls_di = conf.get_urls_di(conf.get("nearest_months"))
        process_data(browser, conf, urls_di)

        logging.info("Finished a crawling run")
    finally:
        browser.quit()
        logging.info("Sleeping for " + str(conf.get("interval")) + " seconds")
        sleep(conf.get("interval"))


def live_worker(opts):
    while True:
        worker(opts)


def main():

    opts = argparser()
    daemonize(opts)

    if opts.one_off:
        worker(opts)
    elif not opts.one_off:
        live_worker(opts)


if __name__ == "__main__":
    main()
