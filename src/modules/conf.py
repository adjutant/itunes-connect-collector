import toml
from os.path import isdir, isfile, join
from modules.es import ESConnector
from modules.timer import get_nearest_months
from modules.itertools import product


class BaseConfig():
    '''
    This is a general configuration validation class.
    '''

    def __init__(self, directory):
        self.directory = directory

        self.conf_files = {"warehouse": "warehouse.conf",
                           "daemon": "daemon.conf",
                           "itunes-connect": "itunes-connect.conf"}

    # This function goes through a list of configuration files
    # as defined in self.conf_files and check if all files exist
    def _check(self):
        returncode = 0
        for conf_file in self.conf_files.values():
            if not isfile(join(self.directory, conf_file)):
                print("Error:" + self.directory + '/' +
                      conf_file + " doesn't exist")
                returncode = 1
        return returncode

    # This function has two features:
    # - Checks if configuration directory exist
    # - List any mising configuration files
    def validate(self):
        if not isdir(self.directory):
            raise Exception(self.directory + " doesn't exist")
        else:
            conf_check = self._check()
            if conf_check != 0:
                raise Exception("Missing configuration file(s).")

    def get(self, key):
        with open(join(self.directory, self.conf_files[key])) as f:
            config = toml.loads(f.read())
        return config


class LoadConfig():
    '''
    This class load configuration from BaseConfig() and makes
    a mapping for those. It also provide 2 public methods to get
    configurations with self.get() and override configurations
    with self.override()
    '''

    def __init__(self, config_path):

        base = BaseConfig(config_path)
        base.validate()

        warehouse = base.get("warehouse")
        daemon = base.get("daemon")
        collector = base.get("itunes-connect")

        # This is an internal mapping, thus the name _mapping.
        # It contains all the ugliness and hardcodes for
        # the rest of the program to be hardcode-free
        self._mapping = {
            "source": warehouse["common"]["source"],

            "record_di": warehouse["records"]["daily-installations"],
            "record_crashes": warehouse["records"]["crashes"],
            "record_dau": warehouse["records"]["daily-active-users"],

            "csv_path_di": join(warehouse["dw"]["csv"],
                                warehouse["records"]["daily-installations"]),
            "csv_path_crashes": join(warehouse["dw"]["csv"],
                                     warehouse["records"]["crashes"]),
            "csv_path_dau": join(warehouse["dw"]["csv"],
                                 warehouse["records"]["daily-active-users"]),

            "record_keys_di": warehouse["record_keys"]["di"],
            "record_keys_crashes": warehouse["record_keys"]["crashes"],
            "record_keys_dau": warehouse["record_keys"]["dau"],

            "conn_string": warehouse["dw"]["conn"],
            "dw_conn": ESConnector(warehouse["dw"]["conn"]).es,

            "log_dir": join(daemon["log_path"], warehouse["common"]["source"]),
            "log_file": join(daemon["log_path"], warehouse["common"]["source"],
                             daemon["log_file"]),

            "timeout": daemon["timeout"],
            "graceful": daemon["graceful_interval"],
            "interval": daemon["interval"],
            "nearest_months": daemon["nearest_months"],

            "el_login_frame": collector["elements"]["login_frame"],
            "el_account": collector["elements"]["account"],
            "el_password": collector["elements"]["password"],
            "el_login": collector["elements"]["login"],
            "el_login_completed": collector["elements"]["login_completed"],
            "el_content_loaded": collector["elements"]["content_loaded"],
            "el_body": collector["elements"]["body"],

            "url_login": collector["urls"]["login"],
            "url_di": collector["urls"]["di"],

            "cred_account": collector["creds"]["account"],
            "cred_password": collector["creds"]["password"],

            "app_id_1": collector["app_ids"]["app1"],
            "app_id_2": collector["app_ids"]["app2"],

            "cc_uk": collector["country_codes"]["uk"],
            "cc_us": collector["country_codes"]["us"],
            "cc_ca": collector["country_codes"]["ca"],
            "inv_cc": {v: k for k, v in collector["country_codes"].items()}
        }

    def get(self, *keys):
        ''' This method returns a value for 1 key or a tuple
        of multiple values for multiple keys.
        '''

        if len(keys) == 1:
            for key in keys:
                return self._mapping[key]

        elif len(keys) > 1:
            results = []

            for key in keys:
                value = self._mapping[key]
                results.append(value)

            return tuple(results)

        elif len(keys) == 0:
            raise TypeError("Expecting at least 1 positional argument")

    def override(self, key, value):
        ''' This method overrides a configuration loaded from file by
        another value. Useful for agrparser parameters.
        '''
        self._mapping[key] = value

    # Below is pure ugliness to workaround for the current product()
    # TODO: Re-implement product() completely to remove this crap
    def _urls_di_formatter(self, urls, url, keys, months, app, countries):

        for values in product(months, (app,), countries):
            fields = dict(zip(keys, values))
            fields["url_di"] = url.format(**fields)

            urls.append(fields)

    def get_urls_di(self, amount):

        urls = []
        url = self.get("url_di")

        months = get_nearest_months(amount)
        keys = ["timestamp_month", "app_id", "country_code"]

        self._urls_di_formatter(urls, url, keys, months,
                                self.get("app1"),
                                self.get("cc_us", "cc_ca"))

        self._urls_di_formatter(urls, url, keys, months,
                                self.get("app2"),
                                (self.get("cc_uk"),))

        return urls
