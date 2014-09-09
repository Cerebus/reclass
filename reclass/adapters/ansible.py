#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of reclass (http://github.com/madduck/reclass)
#
# IMPORTANT NOTICE: I was kicked out of the Ansible community, and therefore
# I have no interest in developing this adapter anymore. If you use it and
# have changes, I will take your patch.
#
# Copyright © 2007–14 martin f. krafft <madduck@madduck.net>
# Released under the terms of the Artistic Licence 2.0
#

import os, sys, posix, optparse

from reclass import get_storage, output
from reclass.core import Core
from reclass.errors import ReclassException
from reclass.config import find_and_read_configfile, get_options
from reclass.version import *
from reclass.constants import MODE_NODEINFO

def node_to_node(nodeinfo):
    """
    convert reclass node to Ansible host_vars
    """
    # Massage and shift the data like Ansible wants it
    nodeinfo['parameters']['__reclass__'] = nodeinfo['__reclass__']
    for i in ('classes', 'applications'):
        nodeinfo['parameters']['__reclass__'][i] = nodeinfo[i]
    return nodeinfo['parameters']

def cli():
    try:
        # this adapter has to be symlinked to ansible_dir, so we can use this
        # information to initialise the inventory_base_uri to ansible_dir:
        ansible_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

        defaults = {'inventory_base_uri': ansible_dir,
                    'pretty_print' : True,
                    'output' : 'json',
                    'applications_postfix': '_hosts',
                    'no_meta': False
                   }
        defaults.update(find_and_read_configfile())

        def add_ansible_options_group(parser, defaults):
            group = optparse.OptionGroup(parser, 'Ansible options',
                                         'Ansible-specific options')
            group.add_option('--applications-postfix',
                             dest='applications_postfix',
                             default=defaults.get('applications_postfix'),
                             help='postfix to append to applications to '\
                                  'turn them into groups')
            group.add_option('--pre-1.3',
                             dest='no_meta', action='store_true',
                             help='make adapter compatible with Ansible '
                                  'before 1.3')
            parser.add_option_group(group)

        options = get_options(RECLASS_NAME, VERSION, DESCRIPTION,
                              inventory_shortopt='-l',
                              inventory_longopt='--list',
                              inventory_help='output the inventory',
                              nodeinfo_shortopt='-t',
                              nodeinfo_longopt='--host',
                              nodeinfo_dest='hostname',
                              nodeinfo_help='output host_vars for the given host',
                              add_options_cb=add_ansible_options_group,
                              defaults=defaults)

        storage = get_storage(options.storage_type, options.nodes_uri,
                              options.classes_uri)
        class_mappings = defaults.get('class_mappings')
        reclass = Core(storage, class_mappings)

        if options.mode == MODE_NODEINFO:
            data = node_to_node(reclass.nodeinfo(options.hostname))
        else:
            data = reclass.inventory()
            # Ansible inventory is only the list of groups. Groups are the set
            # of classes plus the set of applications with the postfix added:
            groups = data['classes']
            apps = data['applications']
            if options.applications_postfix:
                postfix = options.applications_postfix
                groups.update([(k + postfix, v) for k, v in apps.iteritems()])
            else:
                groups.update(apps)

            if options.no_meta:
                data = groups
            else:
                hostvars = dict()
                for node, nodeinfo in data['nodes'].items():
                    hostvars[node] = node_to_node(nodeinfo)
                data = groups
                data['_meta'] = {'hostvars': hostvars}

        print output(data, options.output, options.pretty_print)

    except ReclassException, e:
        e.exit_with_message(sys.stderr)

    sys.exit(posix.EX_OK)

if __name__ == '__main__':
    cli()
