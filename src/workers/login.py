from workers.scrapers import el_locate
import logging


def login(browser, conf):
    ''' This function supports the login to iTune Connect.

    Take:
    3 parameters: browser, creds, elements
    - browser: a session of Selenium WebDriver
    - creds: a dict of credentials in the format of
            { "login_url" : url_string,
              "account": account,
              "password": password }
    - elements: a dict contains of locators of the login page's
                HTML/CSS elements, in the format of
                { "login_frame" : [ method, value ],
                  "account" : [ method, value ],
                  "password" : [ method, value ],
                  "login" : [ method, value ],
                  "login_completed" : [ method, value ] }

    Return: None

    Notes: PhantomJS doesn't do redirection after logging in like Chrome.
    There is a workaround implemented for now.
    '''

    # Initiate a browser session using Selenium WebDriver PhantomJS
    browser.get(conf.get("url_login"))

    timeout = conf.get("timeout")
    log_dir = conf.get("log_dir")

    # Wait until login widget is successfully loaded.
    # Switch to login widget once ready.
    el_locate(browser, timeout, log_dir, conf.get("el_login_frame"))
    browser.switch_to.frame(conf.get("el_login_frame")[1])

    # Wait further for login input fields to be loaded,
    # then send over credentials for login.
    locator = el_locate(browser, timeout, log_dir, conf.get("el_account"))
    locator.send_keys(conf.get("cred_account"))

    locator = el_locate(browser, timeout, log_dir, conf.get("el_password"))
    locator.send_keys(conf.get("cred_password"))

    locator = el_locate(browser, timeout, log_dir, conf.get("el_login"))
    locator.click()

    # Re-fetch the page as PhantomJS doesn't do redirect like Chrome
    # TODO: Need to know WHY. This is a workaround
    el_locate(browser, timeout, log_dir, conf.get("el_login_frame"))
    browser.get(conf.get("url_login"))

    # Wait until login process is completed
    el_locate(browser, timeout, log_dir, conf.get("el_login_completed"))

    logging.info("Finished logging in")
