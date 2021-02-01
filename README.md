This is a fork from https://github.com/ansible-collections/community.general/blob/main/scripts/inventory/vagrant.py with some modifications to work with newer Vagrant releases. 

Changes include:

- the directory name where the Vagrantfile lies is used as `ansible_host`

- reads `vagrant global-status --prune` to find running VMs 


Sample calls:

```
ansible -i vagrant-ansible-dynamic-inventory/vagrant-inventory.py --list-hosts all
ansible -i vagrant-ansible-dynamic-inventory/vagrant-inventory.py -m ping all
vagrant-ansible-dynamic-inventory/vagrant-inventory.py --list
vagrant-ansible-dynamic-inventory/vagrant-inventory.py --host=abcdefg
```

Might be useful to disable strict host key checking before:
```
export ANSIBLE_HOST_KEY_CHECKING=False
```
