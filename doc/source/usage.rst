=============
Using reclass
=============
.. todo::

  With |reclass| now in Debian, as well as installable from source, the
  following should be checked for path consistency…

Command Line Interface
------------

For information on how to use |reclass| directly, call ``reclass --help``
and study the output, or have a look at its :doc:`manual page <manpage>`.

The three options, ``--inventory-base-uri``, ``--nodes-uri``, and
``--classes-uri`` together specify the location of the inventory. If the base
URI is specified, then it is prepended to the other two URIs, unless they are
absolute URIs. If these two URIs are not specified, they default to ``nodes``
and ``classes``. Therefore, if your inventory is in ``/etc/reclass/nodes`` and
``/etc/reclass/classes``, all you need to specify is the base URI as
``/etc/reclass`` — which is actually the default (specified in
``reclass/defaults.py``).

If you've installed |reclass| from source as per the :doc:`installation
instructions <install>`, try to run it from the source directory like this::

  $ reclass -b examples/ --inventory
  $ reclass -b examples/ --nodeinfo localhost

This will make it use the data from ``examples/nodes`` and
``examples/classes``, and you can surely make your own way from here.

On Debian-systems, use the following::

  $ reclass -b /usr/share/doc/reclass/examples/ --inventory
  $ reclass -b /usr/share/doc/reclass/examples/ --nodeinfo localhost

More commonly, however, use of |reclass| will happen indirectly, and through
so-called adapters. The job of an adapter is to translate between different
invocation paradigms, provide a sane set of default options, and massage the
data from |reclass| into the format expected by the automation tool in use.
Please have a look at the respective README files for these adapters, i.e.
for :doc:`Salt <salt>`, for :doc:`Ansible <ansible>`, and for :doc:`Puppet
<puppet>`.

.. include:: substs.inc


Python
------------

More verbose example how you can use reclass directly from python.

.. code-block:: python

    from __future__ import absolute_import

    from reclass import get_storage, output
    from reclass.core import Core

    # note: all this stuff can be imported from reclass.defaults import *
    STORAGE_TYPE = 'yaml_fs'
    NODES_URI = 'nodes'
    CLASSES_URI = 'classes'
    PRETTY_PRINT = True
    OUTPUT = 'yaml'
    RECLASS_NAME = "reclass"
    
    RECLASS_DIR = "/srv/reclass"

    node_uri = "/".join([RECLASS_DIR, RECLASS_NAME, NODES_URI]
    classes_uri = "/".join([RECLASS_DIR, RECLASS_NAME, CLASSES_URI]
    
    storage = get_storage(STORAGE_TYPE, node_uri, classes_uri)

    reclass = Core(storage, None)

    nodes = reclass.inventory()["nodes"]

    print output(nodes, OUTPUT, PRETTY_PRINT)


With this simple class can you manage X reclasses in one directory. Easily can you extend this class how you want.

.. code-block:: python

    from __future__ import absolute_import

    from reclass import get_storage, output
    from reclass.core import Core
    from reclass.defaults import *

    RECLASS_DIR = "/srv/reclass"

    class ReclassUtils(object):

        def get_reclass(self, name):
            """return instance of reclass 
            output(get_reclass("reclass").nodeinfo("foo.bar.cz"), "json". PRETTY_PRINT)
            """

            storage = get_storage(STORAGE_TYPE, "/".join([RECLASS_DIR, name, NODES_URI]),
                                  "/".join([RECLASS_DIR, name, CLASSES_URI]))

            reclass = Core(storage, None)

            return reclass

        def nodes(self, reclass):
            reclass = self.get_reclass(reclass)
            return reclass.inventory()["nodes"]

        def applications(self, reclass):
            reclass = self.get_reclass(reclass)
            return reclass.inventory()["applications"]

        def classes(self, reclass):
            reclass = self.get_reclass(reclass)
            return reclass.inventory()["classes"]

        def nodeinfo(self, reclass, node_name):
            return self.get_reclass(reclass).nodeinfo(node_name)

    reclass_utils = ReclassUtils()

    # print all nodes
    print reclass_utils.get_reclass("reclass").inventory()["nodes"]

    # less verbose example
    print reclass_utils.nodes("reclass")

    print reclass_utils.nodeinfo("reclass", "foo.bar.cz")