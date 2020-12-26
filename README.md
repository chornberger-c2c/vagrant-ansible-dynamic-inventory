This is a fork from the official ansible repository with some modifications.

Reads `vagrant global-status` to find running VMs and creates a dynamic inventory to be used by ansible.


`ansible -i vagrant-ansible-dynamic-inventory/vagrant-inventory.py --list-hosts all`

`ansible -i vagrant-ansible-dynamic-inventory/vagrant-inventory.py -m ping all`

`vagrant-ansible-dynamic-inventory/vagrant-inventory.py --list`

`vagrant-ansible-dynamic-inventory/vagrant-inventory.py --host=abcdef`
