import requests
from classes.httpclient import HttpClient


class VeevaDocument:
    def __init__(self, name: str, doc_id: str, client: HttpClient):
        self.name = name
        self.doc_id = doc_id
        self.client = client

    def download(self) -> bytes:
        with requests.Session() as session:
            return self.client.http_get_file(self.doc_id, session)
            