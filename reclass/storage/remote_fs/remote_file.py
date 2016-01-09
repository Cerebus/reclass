#
# -*- coding: utf-8 -*-
#
# This file is part of reclass (http://github.com/madduck/reclass)
#
# Copyright © 2007–14 martin f. krafft <madduck@madduck.net>
# Released under the terms of the Artistic Licence 2.0
#
from reclass import datatypes
import yaml
import os
from reclass.errors import NotFoundError
from .client import client


class RemoteFile(object):

    def __init__(self, data=dict()):
        ''' Initialise a yamlfile object '''

        self._data = data

    def load_data(self, name):
        '''make request'''
        self._path = client.get_endpoint() + name
        self._data = client.request(name)

    def get_entity(self, name=None, default_environment=None):

        self.load_data(name)

        classes = self._data.get('classes')
        if classes is None:
            classes = []
        classes = datatypes.Classes(classes)

        applications = self._data.get('applications')
        if applications is None:
            applications = []
        applications = datatypes.Applications(applications)

        parameters = self._data.get('parameters')
        if parameters is None:
            parameters = {}
        parameters = datatypes.Parameters(parameters)

        env = self._data.get('environment', default_environment)

        if name is None:
            name = self._path

        return datatypes.Entity(classes, applications, parameters,
                                name=name, environment=env,
                                uri='remote_fs://{0}'.format(name))

    def __repr__(self):
        return '<{0} {1}, {2}>'.format(self.__class__.__name__, self._path,
                                       self._data.keys())
