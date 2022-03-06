#!/usr/bin/env python

import os
import subprocess
import re

from ansible.module_utils._text import to_text
from ansible.plugins.inventory import BaseInventoryPlugin

class InventoryModule(BaseInventoryPlugin):

    NAME = 'vagrant'
    VAGRANT = "vagrant"

    def __init__(self):

        self.virtualbox_path = None
        super(InventoryModule, self).__init__()

    def _query_vagrant_data(self, vagrantline):

        vagrantfile = vagrantline.split()[-2].strip() + '/Vagrantfile'
        file = open(vagrantfile, "r")
        for line in file:
            os = re.search(r"config.vm.box.*\"(.*)\/(.*)\"", line)
            if os:    
                os_outer = str(os.group(1))
                os_inner = str(os.group(2))
                return(os_outer, os_inner)

    def _query_boxname(self, vagrantline):

        dirname = vagrantline.split()[-2].strip()
        boxname = dirname.split('/')[-1]
        return(boxname)

    def _populate_from_source(self, source_data, using_current_cache=False):

        if using_current_cache:
            self._populate_from_cache(source_data)
            return source_data

        cacheable_results = {'_meta': {'hostvars': {}}}

        hostvars = {}
        prevkey = pref_k = ''
        current_host = None

        netinfo = self.get_option('network_info_path')

        for line in source_data:
            line = to_text(line)
            #if ':' not in line:
            #    continue
            try:
                k, v = line.split('')
            except Exception:
                continue

            if k.strip() == '':
                continue

            v = v.strip()

            if "default" not in v:
                continue

            current_host = _query_boxname(v)
 
            if current_host not in hostvars:
                _query_vagrant_data(v)
                hostvars[current_host] = {}
                self.inventory.add_host(current_host)

        
    def verify_file(self, path):
        ''' return true/false if this is possibly a valid file for this plugin to consume '''
        valid = False
        if super(InventoryModule, self).verify_file(path):
            # base class verifies that file exists and is readable by current user
            if path.endswith(('vagrant.yaml', 'vagrant.yml')):
                valid = True
        return valid

    def parse(self, inventory, loader, path, cache=True):

        try:
            self.vagrant_path = get_bin_path(self.VAGRANT)
        except ValueError as e:
            raise AnsibleParserError(e)

        super(InventoryModule, self).parse(inventory, loader, path)

        cache_key = self.get_cache_key(path)

        config_data = self._read_config_data(path)

        self._consume_options(config_data)

        source_data = None
        if cache:
            try:
                source_data = self._cache[cache_key]
            except KeyError:
                update_cache = True

        if not source_data:
            running = self.get_option('running_only')

            cmd = [self._vagrant_path, 'global-status', '--prune']
            
            try:
                p = Popen(cmd, stdout=Pipe)
            except Exception as e:
                raise AnsibleParserError(to_native(e))

            source_data = p.stdout.read().splitlines()

        using_current_cache = cache and not update_cache
        cacheable_results = self._populate_from_source(source_data, using_current_cache)

        if update_cache:
            self._cache[cache_key] = cacheable_results
        
