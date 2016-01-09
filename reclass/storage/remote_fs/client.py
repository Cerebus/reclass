
import requests
import yaml
from reclass.config import find_and_read_configfile


class RemoteReclassClient(object):

    '''Set ``remote_fs_url`` url to your backend.'''

    def get_endpoint(self):
        return self.config.get('remote_fs_url', 'http://localhost/reclass/')

    def request(self, path):

        full_path = self.get_endpoint() + path

        response = requests.get(full_path)

        return self.process_response(response)

    def process_response(self, response):
        '''Extract error as exception and rendered as yaml body
        '''

        data = response.json()

        if 'error' in data:
            raise Exception(data['error'])

        if 'rendered' in data and data['rendered']:
            return yaml.load(data['rendered'])

        return data

    @property
    def config(self):
        return find_and_read_configfile()

client = RemoteReclassClient()
