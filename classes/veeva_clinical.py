import os
import requests
import io

from typing import Optional, List
from classes.veeva_document import VeevaDocument
from classes.httpclient import HttpClient

class VeevaClinical:
    def __init__(self, vault_dns: str, user: str, password: str, verify: Optional[bool] = True):
        session_id = self.__get_session_id(user, password, vault_dns)
        self.session_id = session_id

        self.client = HttpClient(vault_dns, session_id, verify)

    def __get_session_id(self, user: str, password: str, vault_dns: str) -> str:
        return HttpClient.login(vault_dns, user, password)
    

    def list_all_files(self) -> List[VeevaDocument]:
        with requests.Session() as session:
            result = self.client.http_get('/objects/documents', session=session)
            if result['responseStatus'] != 'SUCCESS':
                if 'errors' in result:
                    raise Exception(f'Failed to retrieve documents with error(s):\n{'\n'.join(result['errors'])}')
                else:
                    raise Exception('Failed to retrieve documents')
            
            files = result['documents']
            return [VeevaDocument(file['document']['filename__v'], file['document']['id'], self.client) for file in files]
        

    def upload_file2(self, file: io.BufferedReader, file_name: str, overwrite: Optional[bool] = True, creation_params: Optional[dict]={}):        
        #now create a file, references the staging file
        create_payload = {
            'file': (file_name, file, "application/octet-stream"),
            'name__v': (None, file_name),
        }

        for key in creation_params:
            create_payload[key]=(None, creation_params[key])

        return self.client.http_post('/objects/documents', files = create_payload)


    def upload_file(self, file: io.BufferedReader, file_name: str, overwrite: Optional[bool] = True, creation_params: Optional[dict]={}):        
        # create folder if not exists
        try:
            payload = {
                'kind': (None,'folder'),
                'path': (None, 'textual_staging'),
                'overwrite': (None, False)
            }
            folder_creation_response = self.client.http_post('/services/file_staging/items', files=payload)
            print(folder_creation_response)
        except:  # noqa: E722
            pass
        
        
        file_size_in_bytes = os.fstat(file.fileno()).st_size

        path = f'textual_staging/{file_name}'
        files = {
            'path': (None, path),
            'size': (None, file_size_in_bytes),
            'overwrite': (None, overwrite)
        }
        create_upload_session_response = self.client.http_post('/services/file_staging/upload', files=files)
        session_id = create_upload_session_response['data']['id']

        #upload to session, can't upload more than 50mb at once. if larger we'll need to loop through file bytes and make multiple calls
        files = {
            "file": (file_name, file, "application/octet-stream"),
        }
        self.client.http_put(f'/services/file_staging/upload/{session_id}', files=files)


        #close upload session
        self.client.http_post(f'/services/file_staging/upload/{session_id}')


        #now create a file, references the staging file
        create_payload = {
            'file': (None, path),
            'name__v': (None, file_name),
        }

        for key in creation_params:
            create_payload[key]=(None, creation_params[key])

        return self.client.http_post('/objects/documents', files = create_payload)
    
    def cancel_upload(self, resumable_session_id: str):
        self.client.http_delete(f'/services/file_staging/upload/{resumable_session_id}')

    def list_upload_session(self) -> List[str]:
        with requests.Session() as session:
            response = self.client.http_get('/services/file_staging/upload', session)
            return [session['id'] for session in response['data']]