This is a fork from https://github.com/ansible-collections/community.general/blob/main/scripts/inventory/vagrant.py with some modifications to work with newer Vagrant releases. 


Basically this an Ansible dynamic inventory for Vagrant boxes.


Changes include:

- the directory name where the Vagrantfile lies is used as `ansible_host`

- reads `vagrant global-status --prune` to find all VMs that are currently running


Host discovery:
```
ansible -i vagrant-ansible-dynamic-inventory/vagrant_inventory.py --list-hosts all
ansible -i vagrant-ansible-dynamic-inventory/vagrant_inventory.py -m ping all
vagrant-ansible-dynamic-inventory/vagrant_inventory.py --list
vagrant-ansible-dynamic-inventory/vagrant_inventory.py --host CentOS8-1
```

Might be useful to disable strict host key checking before:
```
export ANSIBLE_HOST_KEY_CHECKING=False
```

Running a playbook against all running Vagrant boxes:
```
ansible-playbook -i vagrant-ansible-dynamic-inventory/vagrant_inventory.py update.yml
```

Running a playbook against a limited amount of running Vagrant boxes:
```
ansible-playbook -i vagrant-ansible-dynamic-inventory/vagrant_inventory.py --limit CentOS8-1 update.yml
```
