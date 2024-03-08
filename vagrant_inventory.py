#!/usr/bin/env python3

"""
Vagrant external inventory script. Automatically finds the IP of the booted
vagrant vm(s), and returns it under the host group 'vagrant' with either the
machine name or - if set to default - the directory name of the Vagrantfile
as ansible inventory hostname.

Copyright (C) 2013  Mark Mandel <mark@compoundtheory.com>
              2015  Igor Khomyakov <homyakov@gmail.com>
              2021  Christopher Hornberger github.com/chornberger-c2c

GNU General Public License v3.0+ (see LICENSE.md or https://www.gnu.org/licenses/gpl-3.0.txt)
"""

from __future__ import (absolute_import, division, print_function)

import sys
import os.path
import subprocess
import re
import argparse
import json

from collections import defaultdict
from io import StringIO
from ansible.module_utils._text import to_text
from paramiko import SSHConfig

def main():
    """
    Thanks to the spacewalk.py inventory script for giving me the basic structure
    of this.
    """

    global MetaClass
    MetaClass = type

    # Parse command line options
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--list', default=False, dest="list", action="store_true",
                    help="Produce a JSON consumable grouping of Vagrant servers for Ansible")
    parser.add_argument('--host', default=None, dest="host",
                    help="Generate additional host specific details for given host for Ansible")
    options = parser.parse_args()

    global mapping
    mapping = {}

    _GROUP = 'vagrant'  # a default group

    if options.list:
        list_running_boxes()
        ssh_config = get_ssh_config()
        meta = defaultdict(dict)

        for host in ssh_config:
            meta['hostvars'][host] = ssh_config[host]

        print(json.dumps({_GROUP: list(mapping.values()), '_meta': meta}, indent=4))
        sys.exit(0)

    elif options.host:
        list_running_boxes()
        host_id = list(mapping.keys())[list(mapping.values()).index(options.host)]
        print(json.dumps(get_a_ssh_config(host_id,options.host), indent=4))
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(0)

def list_running_boxes():
    """
    List all running vagrant boxes
    """

    output = to_text(subprocess.check_output(["vagrant", "global-status", "--prune"])).split('\n')

    for line in output:
        match = re.search(r"^([a-zA-Z0-9]+)\s+([^\/\ ]+).*(running).+?([^\/]+$)", line)
        if match:
            box_id = str(match.group(1))
            box_name = str(match.group(2))
            box_up = str(match.group(3))
            box_dir = str(match.group(4)).strip()

            if box_name == "default":
                pretty_box_name = box_dir

            else:
                pretty_box_name = box_name

            if box_up == "running":
                mapping[box_id] = pretty_box_name

def get_ssh_config():
    """
    Returns the ssh config for a box
    """

    return dict((v, get_a_ssh_config(k,v)) for k,v in mapping.items())

def get_a_ssh_config(box_id,box_name):
    """
    Gives back a map of all the machine's ssh configurations
    """

    _ssh_to_ansible = [('user', 'ansible_user'),
                ('hostname', 'ansible_host'),
                ('identityfile', 'ansible_private_key_file'),
                ('port', 'ansible_port')]

    output = to_text(subprocess.check_output(["vagrant", "ssh-config", box_id]))
    config = SSHConfig()
    config.parse(StringIO(output))

    host_config = config.lookup(box_name)

    if len(host_config) == 1:
        host_config = config.lookup('default')

    # man 5 ssh_config:
    # > It is possible to have multiple identity files ...
    # > all these identities will be tried in sequence.

    for identity in host_config['identityfile']:
        if os.path.isfile(identity):
            host_config['identityfile'] = identity

    return dict((v, host_config[k]) for k, v in _ssh_to_ansible)

if __name__ == "__main__":
    main()
