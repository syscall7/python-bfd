
--------------------------------------------------------------------------------
CODA Prototpye Documentation
--------------------------------------------------------------------------------

DEPENDENCIES
============

Setting up the CODA prototype requires the following dependencies:

  * Ubuntu 14.04.1 LTS
  * Apache
  * MySQL
  * Python 2.7
  * Node.js
  * Binutils Source Code (binutils-2.24.51.tar.bz2)
  * libxml2-dev
  * libxslt1-dev
  * subversion
  * texinfo
  * patch
  * bzip2
  * gcc
  * make
  * autoconf
  * python-pip
  * python-virtualenv
  * libpython-dev
  * libssl-dev
  * libffi-dev
  * cython
  * libapache2-mod-wsgi
  * libmysqlclient-dev
  * The following Python modules are required for the CODA server:
      * Cython==0.20.1
      * Django==1.6.2
      * MySQL-python==1.2.5
      * argparse==1.2.1
      * django-allauth==0.18.0
      * django-appconf==0.6
      * django-compressor==1.4
      * djangorestframework==2.3.13
      * dnspython==1.11.1
      * nose==1.3.1
      * oauthlib==0.6.1
      * python-openid==2.2.5
      * requests==2.2.1
      * requests-oauthlib==0.4.0
      * six==1.6.1
      * wsgiref==0.1.2
      * gsutil==3.42
      * django-google-storage==0.3
      * bidict==0.1.5
      * ipython==2.2.0
      * beautifulsoup4==4.3.2
      * lxml==3.4.0

INSTALLING CODA
===============

Ensure the dependencies are installed before proceeding.

ODA_SRC_DIR=/home/<user>
ODA_INSTALL_DIR=/var/www/oda

# Build and install our custom version of the BFD library
# NOTE: You will have to supply a version of binutils-2.24.51.tar.bz2 unless
#       you are connected to the Internet
cd $CODA_SRC_DIR/bfd
sudo ./build_bfd.sh

# Build the CODA BFD python module
cd $CODA_SRC_DIR/bfd
$CODA_INSTALL_DIR/env/bin/python setup.py install

# Setup the python virtual environment
sudo mkdir $CODA_INSTALL_DIR
sudo virtualenv $CODA_INSTALL_DIR/env

# Copy the CODA source code to the WWW directory and install the Python requirements
sudo mkdir $CODA_INSTALL_DIR/site
cd $CODA_INSTALL_DIR/site/
cp -R $CODA_SRC_DIR/oda_workspace/* .
sudo $CODA_INSTALL_DIR/env/bin/pip install -r requirements.txt
sudo chown -R www-data $CODA_INSTALL_DIR
sudo chgrp -R www-data $CODA_INSTALL_DIR

# Install NodeJS
curl -sL https://deb.nodesource.com/setup | sudo bash -
sudo apt-get install nodejs

# Instal MySQL
# Setup apache and mysql
echo mysql-server mysql-server/root_password password '***REMOVED***' | sudo debconf-set-selections
echo mysql-server mysql-server/root_password_again password '***REMOVED***' | sudo debconf-set-selections
sudo apt-get install mysql-server libmysqlclient-dev -y

# Setup the database for CODA
echo "create database odapython2;" | mysql --user=root --password='***REMOVED***'
sudo $CODA_INSTALL_DIR/env/bin/python manage.py syncdb --settings=oda.settings.production
sudo $CODA_INSTALL_DIR/env/bin/python manage.py setup_oda --settings=oda.settings.production
sudo $CODA_INSTALL_DIR/env/bin/python manage.py setup_openid --settings=oda.settings.production -m prod

# Fixup the wsgi script to point to our install location
perl -p -i -e 's/\$\{([^}]+)\}/defined $ENV{$1} ? $ENV{$1} : $&/eg' < $CODA_INSTALL_DIR/site/oda.wsgi  > $CODA_INSTALL_DIR/site/oda.wsgi_2
mv $CODA_INSTALL_DIR/site/oda.wsgi_2 $CODA_INSTALL_DIR/site/oda.wsgi
perl -p -i -e 's/\$\{([^}]+)\}/defined $ENV{$1} ? $ENV{$1} : $&/eg' < $CODA_INSTALL_DIR/site/apache_odaweb.site > $CODA_INSTALL_DIR/site/onlinedisassembler.conf
mv $CODA_INSTALL_DIR/site/onlinedisassembler.conf /etc/apache2/sites-available/

# Setup the Apache VirtualHost
Copy the following contents to /etc/apache2/sites-available/default

    <VirtualHost *:80>
            ServerAdmin admin@onlinedisassembler.com

            Alias /static/ /var/www/oda2/webapp/odaweb/static/
            Alias /static2/ /var/www/oda2/webapp/odaweb/static/
            WSGIScriptAlias / /var/www/oda2/webapp/oda.wsgi

            # AVD 4/9/13 - hard limit for file upload size
            LimitRequestBody 7097152

            ErrorLog ${APACHE_LOG_DIR}/error.log

            # Possible values include: debug, info, notice, warn, error, crit,
            # alert, emerg.
            LogLevel warn

            CustomLog ${APACHE_LOG_DIR}/access.log combined
    </VirtualHost>

# Create some CODA directories
sudo mkdir -p /var/oda/uploads
sudo mkdir -p /var/oda/cache
sudo chown -R www-data /var/oda
sudo chgrp -R www-data /var/oda

# Install Cuckoo with ODA modifications

1. Get the Cuckoo source

You'll need to download two Cuckoo repositories: a) the main Cuckoo repo, and b) the Cuckoo monitor DLL repo.

  # create your cuckoo directory
  mkdir ~/cuckoo_sandbox
  cd ~/cuckoo_sandbox

  # cuckoo main
  git clone https://github.com/cuckoobox/cuckoo
  pushd cuckoo
  git checkout -q 239fb440b05038d0016cb416bc1c1768a0870100
  popd

  # cuckoo monitor DLL (not necessary if using pre-built ODA Cuckoo DLL)
  git clone https://github.com/cuckoobox/cuckoomon.git
  pushd cuckoomon
  git checkout -q cccba1ae19755ab5e45327a9683d230897269e41
  popd

2. Apply the ODA patches

  # Get the Cuckoo patches
  cd ~/cuckoo_sandbox
  svn co svn://svn.onlinedisassembler.com/oda/ODA/trunk/cuckoo/patches

  # apply the analyzer patch
  pushd ~/cuckoo_sandbox/cuckoo
  patch --verbose -u -p1 < ../patches/analyzer.patch
  popd

  # apply the REST API patch
  pushd ~/cuckoo_sandbox/cuckoo
  patch --verbose -u -p1 < ../patches/rest_api.patch
  popd

  # apply the cuckoo monitor DLL patch
  # NOTE: Not necessary if using pre-built ODA Cuckoo DLL
  pushd ~/cuckoo_sandbox/cuckoomon
  patch --verbose -u -p1 < ../patches/cuckoomon.patch
  popd

3. Build the Cuckoo monitor DLL

  NOTE: You can skip this step by using ODA's pre-built version of
        cuckoomon.dll ($CODA_SRC_DIR/cuckoo/cuckoomon.dll)

  To build from source, you'll first have to install a mingw environment:
      sudo apt-get install mingw32

  Next, build the DLL:
      pushd ~/cuckoo_sandbox/cuckoomon
      make

4. Move the Cuckoo monitor DLL into Cuckoo

  The ODA cuckoomon.dll file (either the ODA pre-built version or the one you
  just built) needs to be moved into cuckoo.

    cp cuckoomon.dll ~/cuckoo_sandbox/cuckoo/analyzer/windows/dll/cuckoomon.dll

5. Install Cuckoo dependencies

  virtualenv cuckoo_python_env
  source cuckoo_python_env/bin/activate
  pip install -r requirements.txt

6. Install VirtualBox

  See the VirtualBox website for installation instructions on your host.

  On Ubuntu, you can install virtualbox with:
    
    sudo apt-get install virtualbox

7. Setup a Windows XP VM image

  Setup a Windows XP VM image in virtual box and configure it for Cuckoo.
  See http://cuckoo.readthedocs.org/en/latest/installation/guest/

  Name the VM image windows_xp_cuckoo_vm to match the 'label' option in
  cuckoo/virtualbox.conf.

8. Configure the VM's networking options

  (GUI) Add the VM image to VirtualBox

  Start VirtualBox and add the Windows XP VM:
 
    Create a host network

    sudo virtualbox
    Click Machine->Add and navigate to the XP VM image.
    Close VirtualBox

  (Headless) Virtual Box Networking

    sudo VBoxManage hostonlyif create
    VBoxManage registervm ~/cuckoo_sandbox/windows_xp_cuckoo_vm/windows_xp_cuckoo_vm.vbox

9. Configure Cuckoo

  Edit ~/cuckoo_sandbox/cuckoo/conf/cuckoo.conf with the following changes:
    
    # Under the [timeouts] section set the default timeout
    default = 10

  Edit ~/cuckoo_sandbox/cuckoo/conf/virtualbox.conf with the following changes:

    # Under the [virtualbox] section
    mode = headless

    # Under the [cuckoo1] section
    label = windows_xp_cuckoo_vm

    # Our Windows XP VM has a snapshot named Snapshot1
    snapshot = Snapshot1

LAUNCHING CODA
==============
# Make sure apache2 is running
  sudo /etc/init.d/apache2 restart

# In another terminal, start the main Cuckoo server:
  cd ~/cuckoo_sandbox/cuckoo
  sudo ./cuckoo -d

# In another terminal, start the Cuckoo API server in another terminal:
  cd ~/cuckoo_sandbox/cuckoo
  sudo ./utils/api.py

# In another terminal, run NodeJS

USING CODA
==============

The typical workflow is to upload a file via the "File->Upload File" menu.
Once the file has been loaded, a user can begin to markup and annotate the
disassembly through right-click context menus as well as keyboard shortcuts.

Collaboration requires signing into CODA with a username and password.

KNOWN LIMITATIONS
=================

  * Setting the ENDIAN option in Live View and File Upload does not work
  * Cannot delete structure definitions
  * Structure definitions do not support pointer types
  * Converting data to code does not recusively follow newly found functions
  * Creating structure definitions can only be triggered through 
  * The links in the Sections Tab do not navigate to the corresponding address
  * The link to Live View does not work, but you can get to it through the
    strcpy example
  * Keyboard shortcuts only work if you have focus in the disassembly window
  * File uploads are currently limited to 2.5 MB (can be changed)
  * Downloading disassembly listing does not work
  * Registering for an account currently throws an exception, but if you sign in
    with the credentials given, you can still get to your account.
