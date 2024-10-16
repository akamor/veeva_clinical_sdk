import requests
from classes.httpclient import HttpClient


class VeevaDocument:
    def __init__(self, name: str, doc_id: str, client: HttpClient):
        self.name = name
        self.doc_id = doc_id
        self.client = client

    def download(self):
        with requests.Session() as session:
            file_content = self.client.http_get_file(self.doc_id, session)
            print(file_content)