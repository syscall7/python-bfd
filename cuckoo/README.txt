
Installing Cuckoo with ODA Modifications
========================================

1. Get the source

You'll need to download two Cuckoo repositories: a) the main Cuckoo repo, and b) the Cuckoo monitor DLL repo.

  # create your cuckoo directory
  mkdir ~/cuckoo_sandbox
  cd ~/cuckoo_sandbox

  # cuckoo main
  git clone https://github.com/cuckoobox/cuckoo
  pushd cuckoo
  git checkout -q 239fb440b05038d0016cb416bc1c1768a0870100
  popd

  # cuckoo monitor DLL
  git clone https://github.com/cuckoobox/cuckoomon.git
  pushd cuckoomon
  git checkout -q cccba1ae19755ab5e45327a9683d230897269e41
  popd

2. Apply the ODA patches

  # Get the Cuckoo patches
  cd ~/cuckoo_sandbox
  svn co svn://svn.onlinedisassembler.com/oda/cuckoo/patches

  # apply the ODA memory dump patch
  pushd ~/cuckoo_sandbox/cuckoo
  patch --verbose -u -p1 < $ODA/cuckoo/patches/procdump.patch
  popd

  # apply the REST API patch
  pushd ~/cuckoo_sandbox/cuckoo
  patch --verbose -u -p1 < $ODA/cuckoo/patches/rest_api.patch
  popd

  # apply the cuckoo monitor DLL patch
  pushd ~/cuckoo_sandbox/cuckoomon
  patch --verbose -u -p1 < $ODA/cuckoo/patches/cuckoomon.patch
  popd

3. Build the Cuckoo monitor DLL

  NOTE: Skip this step by using ODA's pre-built version of cuckoomon.dll.

  First you'll have to install a mingw environment:
      sudo apt-get install mingw32

  Next, build the DLL:
      pushd ~/cuckoo_sandbox/cuckoomon
      make

4. Move the Cuckoo monitor DLL into Cuckoo

  The ODA cuckoomon.dll file (either the ODA pre-built version or the one you
  just built) needs to be moved into cuckoo.

    cp cuckoomon.dll ~/cuckoo_sandbox/cuckoo/analyzer/windows/dll/cuckoomon.dll

5. Install Cuckoo dependencies

  Install required Python libraries:

    sudo apt-get install python-sqlalchemy python-bson

  Install optional packages:

    sudo apt-get install python-dpkt python-jinja2 python-magic python-pymongo python-gridfs python-libvirt python-bottle python-pefile python-chardet

6. Install VirtualBox

  See the VirtualBox website for installation instructions on your host.

  On Ubuntu, you can install virtualbox with:
    
    sudo apt-get install virtualbox

7. Get the VM image

  Grab and extract a copy of the Windows XP VM:
    
    # Download the Windows XP VM from my Google Drive
    https://drive.google.com/a/ransomed.us/file/d/0B6vDgWy-q6DxVFVoTUt0bzFoZDA/edit?usp=sharing

    # Extract the image
    cd ~/cuckoo_sandbox
    tar -xjf windows_xp_cuckoo_vm.tar.bz2

8. Configure Cuckoo

  Edit ~/cuckoo_sandbox/cuckoo/conf/cuckoo.conf with the following changes:
    
    # This should be the IP address of the machine running Cuckoo
    ip = 192.168.1.124

    # use SQLite for ease of use
    connection = sqlite:///cuckoo.db
    
    # set the default timeout
    default = 10

  Edit ~/cuckoo_sandbox/cuckoo/conf/virtualbox.conf with the following changes:

    # Use the Windows XP vm
    machines = windows_xp_cuckoo_vm

    # Specify the IP address of the VM
    ip = 192.168.1.126

Launching Cuckoo
================

Running Cuckoo involves starting the main Cuckoo server as well as the REST
API server.

To start the main Cuckoo server:

  cd ~/cuckoo_sandbox/cuckoo
  sudo ./cuckoo -d

To start the Cuckoo API server in another terminal:

  cd ~/cuckoo_sandbox/cuckoo
  sudo ./utils/api.py

