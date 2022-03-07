#!/usr/bin/env python

import os
import subprocess
import re

from subprocess import Popen, PIPE

from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.errors import AnsibleError, AnsibleParserError
from ansible.module_utils.common.process import get_bin_path
from ansible.module_utils.common.text.converters import to_bytes, to_native, to_text
from ansible.module_utils._text import to_text

class InventoryModule(BaseInventoryPlugin):

    NAME = 'vagrant'
    VAGRANT = "vagrant"

    def __init__(self):

        self.virtualbox_path = None
        super(InventoryModule, self).__init__()

    def _get_structured_inventory(self, inventoryline):

        inventory_data = {}
        dirname = str(inventoryline).split()[-2].strip()
        boxname = str(dirname).split('/')[-1]

        print(boxname)

        inventory_data[boxname]['ssh'] = self._get_a_ssh_config(boxname) 

        vagrantfile = dirname + '/Vagrantfile'
        print(vagrantfile)
        file = open(vagrantfile, "r")
        for line in file:
            os = re.search(r"config.vm.box.*\"(.*)\/(.*)\"", line)
            if os:    
                inventory_data[boxname][family] = str(os.group(1))
                inventory_data[boxname][model] = str(os.group(2))
        self._populate(inventory_data)
    
    def _get_a_ssh_config(box_name):
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


    def verify_file(self, path):
        ''' return true/false if this is possibly a valid file for this plugin to consume '''
        valid = False
        if super(InventoryModule, self).verify_file(path):
            # base class verifies that file exists and is readable by current user
            if path.endswith(('vagrant.yaml', 'vagrant.yml')):
                valid = True
        return valid

    def _populate(self, vagrant_output):
        '''Return hosts and groups'''
        self.myinventory = self._get_structured_inventory(vagrant_output)

        family = []
        model = []
        ssh_parameters = {}

        for hostname,data in self.myinventory.items():
            ssh_parameters =  self._get_a_ssh_config(hostname)
            self.inventory.add_host(host=hostname, group="vagrant")
            self.inventory.set_variable(hostname, ssh_parameters)

    def parse(self, inventory, loader, path, cache):
       '''Return dynamic inventory from source '''
       super(InventoryModule, self).parse(inventory, loader, path, cache)
       # Read the inventory YAML file
       self._read_config_data(path)
       #try:
       #    # Store the options from the YAML file
       #    self.plugin = self.get_option('plugin')
       #except Exception as e:
       #    raise AnsibleParserError('All correct options required: {}'.format(e))
       # Call our internal helper to populate the dynamic inventory

       try:
            self.vagrant_path = get_bin_path(self.VAGRANT)
       except ValueError as e:
            raise AnsibleParserError(e)

       #if not source_data:
       #running = self.get_option('running_only')

       cmd = [self.vagrant_path, 'global-status', '--prune']
            
       try:
           p = Popen(cmd, stdout=PIPE)
       except Exception as e:
           raise AnsibleParserError(to_native(e))

       source_data = str(p.stdout.read())

       for line in source_data:
           matchname = re.search(r"(running.+?)([^\/]+$)", line)
           matcher = re.search(r"^\s*([a-zA-Z0-9]+).*running", line)
           if matcher and matchname:
               self._get_structured_inventory(line)
