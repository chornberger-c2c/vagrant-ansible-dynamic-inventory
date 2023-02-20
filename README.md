[![linting](https://github.com/horni23/vagrant-ansible-dynamic-inventory/actions/workflows/lint.yaml/badge.svg)](https://github.com/horni23/vagrant-ansible-dynamic-inventory/actions/workflows/lint.yaml)


## Origin
This is an Ansible dynamic inventory for Vagrant boxes, forked from https://github.com/ansible-collections/community.general/blob/main/scripts/inventory/vagrant.py

## New features
- the hostname `ansible_host` is the directory name where the Vagrantfile exists

- all running VMs are reachable without setting connection parameters (by reading `vagrant global-status --prune`)

## Settings
Need to disable strict host key checking
```
export ANSIBLE_HOST_KEY_CHECKING=False
```

## Host discovery
```
ansible -i vagrant_inventory.py --list-hosts all 
  hosts (2):
    vm_debian9
    vm_centos8_3
```

```shell
ansible -i vagrant_inventory.py -m ping all
vm_debian9 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    },
    "changed": false,
    "ping": "pong"
}
vm_centos8_3 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/libexec/platform-python"
    },
    "changed": false,
    "ping": "pong"
}
```

```
vagrant_inventory.py --list                  
{
    "vagrant": [
        "vm_debian9", 
        "vm_centos8_3"
    ], 
    "_meta": {
        "hostvars": {
            "vm_centos8_3": {
                "ansible_port": "2222", 
                "ansible_host": "127.0.0.1", 
                "ansible_user": "vagrant", 
                "ansible_private_key_file": "/home/user/workspace/vagrant/vm_centos8_3/.vagrant/machines/default/virtualbox/private_key"
            }, 
            "vm_debian9": {
                "ansible_port": "2200", 
                "ansible_host": "127.0.0.1", 
                "ansible_user": "vagrant", 
                "ansible_private_key_file": "/home/user/workspace/vagrant/vm_debian9/.vagrant/machines/default/virtualbox/private_key"
            }
        }
    }
}
```

```
vagrant_inventory.py --host vm_debian9        
{
    "ansible_port": "2200", 
    "ansible_host": "127.0.0.1", 
    "ansible_user": "vagrant", 
    "ansible_private_key_file": "/home/user/workspace/vagrant/vm_debian9/.vagrant/machines/default/virtualbox/private_key"
}
```

## Running a playbook 

### against all running Vagrant boxes:
```
ansible-playbook -i vagrant_inventory.py site.yml
```

### against a limited amount of running Vagrant boxes:
```
ansible-playbook -i vagrant_inventory.py --limit vm_debian9 site.yml
```
