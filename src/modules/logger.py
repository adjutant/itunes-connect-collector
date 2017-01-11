import logging


def logger(log_file):
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format='%(asctime)s %(message)s',
                        datefmt='%Y-%m-%d %I:%M:%S %p')
