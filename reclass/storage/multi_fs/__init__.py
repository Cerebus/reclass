
import fnmatch
import os
import sys

import reclass.errors
from reclass.storage import NodeStorageBase
from reclass.storage.yaml_fs.directory import Directory
from reclass.config import find_and_read_configfile


FILE_EXTENSION = '.yml'
STORAGE_NAME = 'multi_fs'


def vvv(msg):
    #print >>sys.stderr, msg
    pass


class ExternalNodeStorage(NodeStorageBase):

    '''Combine more storage backends'''

    def __init__(self, nodes_uri, classes_uri, default_environment=None):
        super(ExternalNodeStorage, self).__init__(STORAGE_NAME)

        self.backends = find_and_read_configfile().get(
            'multi_fs', ['yaml_fs', 'remote_fs'])

        def name_mangler(relpath, name):
            # nodes are identified just by their basename, so
            # no mangling required
            return relpath, name
        self._nodes_uri = nodes_uri
        self._nodes = self._enumerate_inventory(nodes_uri, name_mangler)

        def name_mangler(relpath, name):
            if relpath == '.':
                # './' is converted to None
                return None, name
            parts = relpath.split(os.path.sep)
            if name != 'init':
                # "init" is the directory index, so only append the basename
                # to the path parts for all other filenames. This has the
                # effect that data in file "foo/init.yml" will be registered
                # as data for class "foo", not "foo.init"
                parts.append(name)
            return relpath, '.'.join(parts)
        self._classes_uri = classes_uri
        self._classes = self._enumerate_inventory(classes_uri, name_mangler)

        self._default_environment = default_environment

    nodes_uri = property(lambda self: self._nodes_uri)
    classes_uri = property(lambda self: self._classes_uri)

    def _enumerate_inventory(self, basedir, name_mangler):
        ret = {}

        def register_fn(dirpath, filenames):
            filenames = fnmatch.filter(
                filenames, '*{0}'.format(FILE_EXTENSION))
            vvv('REGISTER {0} in path {1}'.format(filenames, dirpath))
            for f in filenames:
                name = os.path.splitext(f)[0]
                relpath = os.path.relpath(dirpath, basedir)
                if callable(name_mangler):
                    relpath, name = name_mangler(relpath, name)
                uri = os.path.join(dirpath, f)
                if name in ret:
                    E = reclass.errors.DuplicateNodeNameError
                    raise E(self.name, name,
                            os.path.join(basedir, ret[name]), uri)
                if relpath:
                    f = os.path.join(relpath, f)
                ret[name] = f

        d = Directory(basedir)
        d.walk(register_fn)
        return ret

    def get_storage_backend(self, name, **kwargs):
        from reclass.storage.loader import StorageBackendLoader
        storage_class = StorageBackendLoader(name).load()
        return storage_class(self._nodes_uri,
                             self._classes_uri,
                             default_environment=self._default_environment,
                             **kwargs)

    def get_node(self, name):
        for backend_name in self.backends:
            try:
                backend = self.get_storage_backend(backend_name)
            except Exception as e:
                raise e
            else:
                try:
                    result = backend.get_node(name)
                except Exception as exc:
                    print >>sys.stderr, 'Node {} not found in {} with {}'.format(
                        name, backend_name, exc)
                else:
                    return result

        raise NotImplementedError

    def get_class(self, name, nodename=None):

        for backend_name in self.backends:
            try:
                backend = self.get_storage_backend(backend_name)
            except Exception as e:
                raise e
            else:
                try:
                    result = backend.get_class(name, nodename)
                except Exception as exc:
                    print >>sys.stderr, 'Could not foud class {} in {} with {}'.format(
                        name, backend_name, exc)
                else:
                    return result

        raise NotImplementedError

    def enumerate_nodes(self):
        return self._nodes.keys()
