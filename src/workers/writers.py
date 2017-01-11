from modules.timer import get_timeid
from os.path import join
import csv
from dateutil import parser
import logging


def index_es(conf, es, es_index, data, country):
    for entry in data:
        timeid = get_timeid(entry["date"], conf.get("%Y%m%d"))
        es.index(index=es_index,
                 doc_type=country,
                 id=timeid,
                 body=entry)
        logging.info("Indexed " + timeid + "/" + str(entry) + " into " +
                     es_index + "/" + country)


def write_csv(conf, country, data, timestamp):
    directory = join(conf.get("csv_path"), country)
    filename = (conf.get("record") + "." + country + "." + timestamp + ".csv")

    file = join(directory, filename)

    with open(file, 'w', newline='') as csvfile:

        writer = csv.writer(csvfile, delimiter=',', quotechar="'",
                            quoting=csv.QUOTE_MINIMAL)

        writer.writerow(conf.get("record_keys_di"))

        for i in data:
            yyyymmdd = parser.parse(i["date"]).strftime(conf.get("%Y-%m-%d"))
            writer.writerow([yyyymmdd, i["country"], i["installations"]])

        logging.info("Finished writing into " + filename)
