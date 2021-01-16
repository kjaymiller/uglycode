from elasticsearch import Elasticsearch
from elastic_enterprise_search import AppSearch
import os

es_client = Elasticsearch(
    cloud_id=os.environ['ES_CLOUD_ID'],
    http_auth=('elastic', os.environ['ES_AUTH']),
    )

app_search = AppSearch(
    os.environ['APPSEARCH_CLOUD_ID'],
    http_auth=os.environ['SECRET_KEY'],
)

client_search = AppSearch(
    os.environ['APPSEARCH_CLOUD_ID'],
    http_auth=os.environ['SECRET_KEY'],
)
