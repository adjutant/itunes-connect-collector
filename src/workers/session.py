from argparse import ArgumentParser
from selenium.webdriver import PhantomJS
from selenium.webdriver import Chrome
from os.path import join, dirname
from subprocess import Popen, PIPE
from modules.conf import LoadConfig
import os
import sys


def _default_conf_path():
    git_cmd = Popen(["git", "-C", dirname(__file__),
                     "rev-parse", "--show-toplevel"], stdout=PIPE)
    git_path = git_cmd.communicate()[0].rstrip().decode("utf8")
    return join(git_path, "conf/")


def argparser():

    parser = ArgumentParser(description="Data collector for Itunes Connect",
                            usage='%(prog)s [options]')
    parser.add_argument('--debug', action="store_true", dest="debug",
                        help="show program's debug and exit")
    parser.add_argument('-c', '--configdir',
                        metavar='DIR', default=_default_conf_path(),
                        help="use a specific configuration directory; "
                        "default to ${git_path}/conf")
    parser.add_argument('-d', '--daemonize',
                        action="store_true", help="daemonizing the program")
    parser.add_argument('--one-off', action="store_true",
                        help="specify whether to run the program only once")
    parser.add_argument('--nearest-months', metavar='N', type=int,
                        help="override with how many nearest months to take")
    opts = parser.parse_args()

    return opts


def daemonize(opts):
    if opts.daemonize:
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError:
            sys.exit(1)


def _ck_conf(opts):

    config = LoadConfig(opts.configdir)

    if opts.nearest_months:
        config.override("nearest_months", opts.nearest_months)

    return config


def _ck_webdriver(opts):

    if not opts.debug:
        browser = PhantomJS()
    elif opts.debug:
        browser = Chrome()

    return browser


def session_init(opts):
    config = _ck_conf(opts)
    browser = _ck_webdriver(opts)

    return browser, config
