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
from reclass.utils.merge_dicts import merge_dicts

def cli():
    try:
        # this adapter has to be symlinked to ansible_dir, so we can use this
        # information to initialise the inventory_base_uri to ansible_dir:
        ansible_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

        defaults = {'inventory_base_uri': ansible_dir,
                    'pretty_print' : True,
                    'output' : 'json',
                    'applications_postfix': '_hosts'
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
            data = reclass.nodeinfo(options.hostname)
            # Massage and shift the data like Ansible wants it
            data['parameters']['__reclass__'] = data['__reclass__']
            for i in ('classes', 'applications'):
                data['parameters']['__reclass__'][i] = data[i]
            data = data['parameters']

        else:
            data = reclass.inventory()

            # put the only forking logic up here
            if options.applications_postfix:
                postfix = options.applications_postfix
            else:
                postfix = ''
            # instantiate base classes dict
            groups = {groupname: {'hosts': hosts} for groupname, hosts in data.pop('classes').iteritems()}
            # add applications to classes
            groups.update({app + postfix: {'hosts': hosts} for app, hosts in data.pop('applications').iteritems()})
            # instantiate
            hostvars = {node: merge_dicts(
                values['parameters'],
                {'__reclass__': merge_dicts(
                    values['__reclass__'],
                    {'applications': values['applications']},
                    {'classes': values['classes']}
                )}) for node, values in data.pop('nodes').iteritems()}
            for node, parameters in hostvars.iteritems():
                environment = parameters['__reclass__']['environment']
                if environment in groups.keys():
                    groups[environment]['hosts'].append(node)
                else:
                    groups[environment] = {'hosts': [node]}

            data = merge_dicts(groups, {'_meta': {'hostvars': hostvars}})

        print output(data, options.output, options.pretty_print)

    except ReclassException, e:
        e.exit_with_message(sys.stderr)

    sys.exit(posix.EX_OK)

if __name__ == '__main__':
    cli()
#
# -*- coding: utf-8 -*-
#
# This file is part of reclass (http://github.com/madduck/reclass)
#
# Copyright © 2007–14 martin f. krafft <madduck@madduck.net>
# Released under the terms of the Artistic Licence 2.0
#
