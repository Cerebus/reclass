
import requests
import yaml
from reclass.config import find_and_read_configfile

TOKEN_FORMAT = "  Token {0}"


class RemoteReclassClient(object):

    '''Set ``remote_fs_url`` url to your backend 
    and ``remote_fs_token``
    .'''

    def get_endpoint(self):
        return self.config.get('remote_fs_url', 'http://localhost/reclass/')

    @property
    def token(self):
        return self.config.get('remote_fs_token', 'd7d56ca0e9679482')

    def process_headers(self, headers={}):
        headers["Authorization"] = TOKEN_FORMAT.format(self.token)
        return headers

    def request(self, path):

        full_path = self.get_endpoint() + path

        response = requests.get(full_path, headers=self.process_headers({}))

        return self.process_response(response)

    def process_response(self, response):
        '''Extract error as exception and rendered as yaml body
        '''

        data = response.json()

        if 'error' in data:
            raise Exception(data['error'])

        if response.status_code == 401 and 'detail' in data:
            raise Exception(data['detail'])

        if 'rendered' in data and data['rendered']:
            return yaml.load(data['rendered'])

        return data

    @property
    def config(self):
        return find_and_read_configfile()

client = RemoteReclassClient()
