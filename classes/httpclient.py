from typing import Optional
import requests
from urllib3.exceptions import InsecureRequestWarning
from requests_toolbelt.utils import dump

requests.packages.urllib3.disable_warnings(  # type: ignore
    category=InsecureRequestWarning
)

class HttpClient:

    def __init__(self, base_url: str, session_id: str, verify: bool):
        self.base_url = base_url
        self.headers = {
            "Authorization": session_id,
        }
        self.verify = verify

    @staticmethod
    def api_version():
        return 'v24.2'

    @staticmethod
    def login(vault_dns: str, username: str, password: str, verify: Optional[bool] = True) -> str:
        vault_dns.removesuffix('/')
        url = vault_dns + '/api/' + HttpClient.api_version() + '/auth'

        data = dict()
        data['username']=username
        data['password']=password
        data['vaultDNS']=vault_dns
        
        res = requests.post(url, headers={'Accepts':'application/json'}, verify=verify, data=data)

        res.raise_for_status()

        response_body = res.json()
        return response_body['sessionId']
    

    def http_get_file(
        self, doc_id: str, session: requests.Session, params: dict = {}, additional_headers={}) -> bytes:
        """Makes a get request to get a file.

        Parameters
        ----------
        url : str
            URL to make the get request. The URL is appended to self.base_url.
        params: dict
            Passed as the params parameter of the requests.get request.

        """

        url = f"{self.base_url}/api/{HttpClient.api_version()}/objects/documents/{doc_id}/file"
        res = session.get(url, params=params, headers={**self.headers, **additional_headers}, verify=self.verify
        )
        
        try:
            res.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(f"Failed to download document: {doc_id}")
            raise err

        return res.content
    
    def http_get(self, endpoint: str, session: requests.Session, params: dict = {}, additional_headers={}):

        endpoint = endpoint.removesuffix('/').removeprefix('/')
        

        url = f"{self.base_url}/api/{HttpClient.api_version()}/{endpoint}"
        res = session.get(url, params=params, headers={**self.headers, **additional_headers}, verify=self.verify)
        
        res.raise_for_status()

        return res.json()
    
    def http_delete(self, endpoint: str, params={}):
        
        endpoint = endpoint.removesuffix('/').removeprefix('/')
        url = f"{self.base_url}/api/{HttpClient.api_version()}/{endpoint}"
        
        res = requests.delete(
            url, params=params, headers=self.headers, verify=self.verify
        )
        res.raise_for_status()

        if res.content:
            return res.json()
        else:
            return None
    
    def http_post(self, endpoint: str, params={}, data={}, files={}, additional_headers={}, timeout_seconds: Optional[int] = None):
    
    
        endpoint = endpoint.removesuffix('/').removeprefix('/')
        url = f"{self.base_url}/api/{HttpClient.api_version()}/{endpoint}"

        try:
            res = requests.post(
                url,
                params=params,
                json=data,
                headers={**self.headers, **additional_headers},
                verify=self.verify,
                files=files,
                timeout=timeout_seconds
            )
        except requests.exceptions.Timeout:
            raise Exception("Request took too long. Increase timeout?")
        
        data = dump.dump_all(res)
        res.raise_for_status()
        
        if res.content:
            try:
               return res.json()
            except:
                return res.text
        else:
            return None
        
    def http_put(self, endpoint: str, params={}, data={}, files={}, additional_headers={}, timeout_seconds: Optional[int] = None):
    
    
        endpoint = endpoint.removesuffix('/').removeprefix('/')
        url = f"{self.base_url}/api/{HttpClient.api_version()}/{endpoint}"

        try:
            res = requests.put(
                url,
                params=params,
                json=data,
                headers={**self.headers, **additional_headers},
                verify=self.verify,
                files=files,
                timeout=timeout_seconds
            )
        except requests.exceptions.Timeout:
            raise Exception("Request took too long. Increase timeout?")
        
        data = dump.dump_all(res)
        print(data.decode('utf-8'))


        res.raise_for_status()
        
        if res.content:
            try:
               return res.json()
            except:
                return res.text
        else:
            return None