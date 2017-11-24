# python-bfd
Python wrapper for binutils Binary File Descriptor (BFD) library

# Contributing

## Installing prerequisites

* [Vagrant](https://www.vagrantup.com/downloads.html)
* [VirtualBox](https://www.virtualbox.org/wiki/Downloads)

## Launching Vagrant

Launching Vagrant will create a new Ubuntu 16.04 VM in VirtualBox, then
provision using Ansible:
```
vagrant up
```
Once Vagrant has provisioned the VM, you can login using:
```
vagrant ssh
```

## Installing BFD package

Install Python BFD using setup.py (NOTE: Python 3 required):
```
cd bfd
python3 setup.py install --user
```

## Executing tests

Simple tests can be run using python:
```
vagrant ssh
cd bfd/test
./test_mkdir.py
```

# Support or Questions

Please report any [Issues](https://github.com/syscall7/python-bfd/issues/new) and
we'll be happy to look.  Feel free to submit a PR with suggested changes.
