#!/bin/sh
These are rough notes, and you must not mindlessly follow them.

ODA_INSTALL_DIR=/var/www/oda

# Upgrade the server
sudo apt-get update
sudo apt-get upgrade -y

# Install subversion
sudo apt-get install subversion install texinfo patch bzip2 gcc make autoconf  -y

cd ~
svn co svn://svn.onlinedisassembler.com/oda/ODA/trunk/bfd --username --password ***REMOVED***
cd bfd
sudo ./build_bfd.sh

# Setup apache and mysql
echo mysql-server mysql-server/root_password password password | sudo debconf-set-selections
echo mysql-server mysql-server/root_password_again password password | sudo debconf-set-selections

sudo apt-get install apache2 libapache2-mod-wsgi mysql-server libmysqlclient-dev -y
# sudo usermod -aG www-data anthony

# Setup the python environment
sudo apt-get install python-pip python-virtualenv libpython-dev libssl-dev libffi-dev cython -y # for gsutil
sudo mkdir $ODA_INSTALL_DIR
sudo virtualenv $ODA_INSTALL_DIR/env

mkdir $ODA_INSTALL_DIR/site
cd $ODA_INSTALL_DIR/site/
svn co svn://svn.onlinedisassembler.com/oda/ODA/trunk/oda_workspace --username davis --password ***REMOVED*** .
sudo ODA_INSTALL_DIR/env/bin/pip install -r requirements.txt

# Build BFD module
mkdir ~/bfd_python
cd ~/bfd_python
svn co svn://svn.onlinedisassembler.com/oda/ODA/trunk/bfd --username davis --password ***REMOVED*** .
sudo $ODA_INSTALL_DIR/env/bin/python setup.py install

sudo chown -R www-data $ODA_INSTALL_DIR
sudo chgrp -R www-data $ODA_INSTALL_DIR

# Create database
echo "create database odapython2;" | mysql --user=root --password=password

# Setup webapp
sudo svn co svn://svn.onlinedisassembler.com/oda/ODA/tags/v1.2.3/django webapp
sudo chown -R www-data webapp
sudo chgrp -R www-data webapp
# edit webapp/oda_python/settings/production.py and add the server's IP address to ALLOWED_HOSTS
cd /var/www/oda2/webapp
sudo ../env/bin/python manage.py syncdb --settings=oda_python.settings.production
sudo ../env/bin/python manage.py setup_oda --settings=oda_python.settings.production
sudo ../env/bin/python manage.py setup_openid --settings=oda_python.settings.production -m prod

sudo vim /etc/apache2/sites-available/default
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

sudo mkdir -p /var/oda/uploads
sudo mkdir -p /var/oda/cache

sudo chown -R www-data /var/oda
sudo chgrp -R www-data /var/oda

sudo chown -R www-data /var/www/oda2
sudo chgrp -R www-data /var/www/oda2

sudo chown www-data /tmp/oda.log
sudo chgrp www-data /tmp/oda.log

sudo a2ensite default
sudo service apache2 reload



