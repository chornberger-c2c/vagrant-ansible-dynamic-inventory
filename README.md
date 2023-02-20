[![linting](https://github.com/horni23/vagrant-ansible-dynamic-inventory/actions/workflows/lint.yaml/badge.svg)](https://github.com/horni23/vagrant-ansible-dynamic-inventory/actions/workflows/lint.yaml)

# Vagrant Ansible Dynamic Inventory
1. [Origin](#origin)
2. [New features](#new-features)
3. [Settings](#settings)
4. [Host discovery](#host-discovery)
5. [Running a playbook](#running-a-playbook)

## Origin
This is an [Ansible dynamic inventory](https://docs.ansible.com/ansible/latest/inventory_guide/intro_dynamic_inventory.html) for Vagrant boxes, forked from https://github.com/ansible-community/contrib-scripts/blob/main/inventory/vagrant.py

## New features
- scalability
    - no need to manually edit and maintain Ansible inventories if you run one or more Vagrant VMs 
    - all running Vagrant VMs are included (by parsing `vagrant global-status --prune`)
    - connection parameters are automatically added for all running VMs
- readability
    - the hostname `ansible_host` is the directory name where the Vagrantfile is located
    - to distinguish the hosts and to limit the connection to specific hosts, if needed

## Settings
Need to disable strict host key checking
```
export ANSIBLE_HOST_KEY_CHECKING=False
```

## Host discovery

### list running Vagrant VMs (for reference only)
```
vagrant global-status --prune | grep running
a524819  default virtualbox running  /home/user/workspace/vagrant/vm_centos8_3            
70bf4ac  default virtualbox running  /home/user/workspace/vagrant/vm_debian9              
```

### Ansible host discovery
- running hosts appear automatically in the dynamic inventory
- including their ssh connection parameters 
  - port
  - host
  - user
  - ssh private key
- their hostname comes from the directory in which the Vagrantfile is located
```
ansible -i vagrant_inventory.py --list-hosts all 
  hosts (2):
    vm_debian9
    vm_centos8_3
```

```
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

- against all running Vagrant VMs
```
ansible-playbook -i vagrant_inventory.py site.yml
```

- against a limited set of running Vagrant VMs
```
ansible-playbook -i vagrant_inventory.py --limit vm_debian9 site.yml
```
