#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import re

from subprocess import Popen, PIPE

from ansible import constants as C
from ansible.errors import AnsibleParserError
from ansible.module_utils.common.text.converters import to_native, to_text
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
from ansible.module_utils.common.process import get_bin_path

class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    ''' Host inventory parser for ansible using local vagrant. '''

    NAME = 'horni.collection.vagrant'
#    find_box_user =  
#    find_box_box = 

    def __init__(self):
        super(InventoryModule, self).__init__()

    def _populate(self, hosts):
        # Use constructed if applicable
        strict = self.get_option('strict')

        for host in hosts:
            hostname = host['name']
            self.inventory.add_host(hostname)
            for var, value in host.items():
                self.inventory.set_variable(hostname, var, value)

            # Composed variables
            self._set_composite_vars(self.get_option('compose'), host, hostname, strict=strict)

            # Complex groups based on jinja2 conditionals, hosts that meet the conditional are added to group
            self._add_host_to_composed_groups(self.get_option('groups'), host, hostname, strict=strict)

            # Create groups based on variable values and add the corresponding hosts to it
            self._add_host_to_keyed_groups(self.get_option('keyed_groups'), host, hostname, strict=strict)

    def verify_file(self, path):

        valid = False
        if super(InventoryModule, self).verify_file(path):
            file_name, ext = os.path.splitext(path)

            if not ext or ext in C.YAML_FILENAME_EXTENSIONS:
                valid = True

        return valid

    def list_all_boxes(self):
        boxes = {}

        try:
            get_bin_path('vagrant')
        except ValueError as e:
            raise AnsibleParserError('vagrant inventory plugin requires the vagrant cli tool to work {0}'.format(to_native(e)))

        output = to_text(subprocess.check_output(["vagrant", "global-status", "--prune"]), errors='surrogate_or_strict').split('\n')
    
        for line in output:
            dirname = re.search(r"(running.+?)(.[^\/].*)", line)
            if dirname:
                vagrantfile = str(dirname.group(2)).strip() + '/Vagrantfile'
                file = open(vagrantfile, "r")
                for line in file:
                    linematch = re.search(r"config.vm.box.*\"(.*)\/(.*)\"", line)
                    if linematch:    
                        vagrant_user = str(linematch.group(1))
                        vagrant_box = str(linematch.group(2))
        boxes[matchfilename] = vagrant_user + '/' + vagrant_box
        return boxes
    
    def get_ssh_config(self):
        """
        returns the ssh config for a box
        """
        return dict((k, get_a_ssh_config(k)) for k in boxes)

    # get the ssh config for a single box
    def get_a_ssh_config(self, box_name):
        """Gives back a map of all the machine's ssh configurations"""
    
        output = to_text(subprocess.check_output(["vagrant", "ssh-config", box_name]))
        config = SSHConfig()
        config.parse(StringIO(output))
        host_config = config.lookup("default")
    
        # man 5 ssh_config:
        # > It is possible to have multiple identity files ...
        # > all these identities will be tried in sequence.
    
        for identity in host_config['identityfile']:
            if os.path.isfile(identity):
                host_config['identityfile'] = identity
    
        return dict((v, host_config[k]) for k, v in _ssh_to_ansible)
    
        
