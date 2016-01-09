
import yaml
import requests


class RemoteReclassClient(object):

    def get_endpoint(self):
        '''TODO: from config'''
        return 'http://10.10.10.166:80/reclass/'

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

        if 'rendered' in data:
            return yaml.load(data['rendered'])

        return data

client = RemoteReclassClient()
