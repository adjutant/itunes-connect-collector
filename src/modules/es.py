from elasticsearch import Elasticsearch


class ESConnector():

    def __init__(self, conn_str):
        self.es = Elasticsearch([conn_str])
