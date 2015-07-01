#!/bin/sh
set -x
set -e
# These are rough notes, and you must not mindlessly follow them.

ODA_INSTALL_DIR=/var/www/oda

# Upgrade the server
sudo apt-get update
sudo apt-get upgrade -y

install_odaweb ()
{
# Install subversion
sudo apt-get install libxml2-dev libxslt1-dev subversion texinfo patch bzip2 gcc make autoconf python-pip python-virtualenv libpython-dev libssl-dev libffi-dev cython -y

cd ~
svn co svn://svn.onlinedisassembler.com/oda/ODA/trunk/bfd --username davis --password ***REMOVED***
cd bfd
sudo ./build_bfd.sh

sudo apt-get install apache2 libapache2-mod-wsgi libmysqlclient-dev -y

# Setup the python environment
sudo mkdir $ODA_INSTALL_DIR
sudo virtualenv $ODA_INSTALL_DIR/env

sudo mkdir $ODA_INSTALL_DIR/site
cd $ODA_INSTALL_DIR/site/
sudo svn co svn://svn.onlinedisassembler.com/oda/ODA/trunk/oda_workspace --username davis --password ***REMOVED*** .
sudo $ODA_INSTALL_DIR/env/bin/pip install -r requirements.txt

# Build BFD module
mkdir ~/bfd_python
cd ~/bfd_python
svn co svn://svn.onlinedisassembler.com/oda/ODA/trunk/bfd --username davis --password ***REMOVED*** .
sudo $ODA_INSTALL_DIR/env/bin/python setup.py install

# create the log file (must match the log handle file entry in settings/base.py)
touch $ODA_INSTALL_DIR/oda.log
sudo chmod ugo+w /var/www/oda/oda.log

sudo chown -R www-data $ODA_INSTALL_DIR
sudo chgrp -R www-data $ODA_INSTALL_DIR

}

install_node()
{
curl -sL https://deb.nodesource.com/setup | sudo bash -
sudo apt-get install nodejs
}

install_mysql()
{
# Setup apache and mysql
echo mysql-server mysql-server/root_password password '***REMOVED***' | sudo debconf-set-selections
echo mysql-server mysql-server/root_password_again password '***REMOVED***' | sudo debconf-set-selections

sudo apt-get install mysql-server libmysqlclient-dev -y

# edit /etc/mysql/my.cnf and set InnoDB to use a separate file per table as follows:
#   innodb_file_per_table
#   innodb_flush_method=O_DIRECT
#   innodb_log_file_size=1G
#   innodb_buffer_pool_size=4G
# also, you should point the mysqld data dir to a location with enough storage
echo "ERROR: You need to edit /etc/mysql/my.cnf manually!"

}

configure_database()
{
# Create database
echo "create database odapython2;" | mysql --user=root --password='***REMOVED***'
cd $ODA_INSTALL_DIR/site/
sudo $ODA_INSTALL_DIR/env/bin/python manage.py syncdb --settings=oda.settings.production
sudo $ODA_INSTALL_DIR/env/bin/python manage.py setup_oda --settings=oda.settings.production
sudo $ODA_INSTALL_DIR/env/bin/python manage.py setup_openid --settings=oda.settings.production -m prod

}

fixup_wsgi()
{

perl -p -i -e 's/\$\{([^}]+)\}/defined $ENV{$1} ? $ENV{$1} : $&/eg' < $ODA_INSTALL_DIR/site/oda.wsgi  > /tmp/oda.wsgi_2
sudo mv /tmp/oda.wsgi_2 $ODA_INSTALL_DIR/site/oda.wsgi

perl -p -i -e 's/\$\{([^}]+)\}/defined $ENV{$1} ? $ENV{$1} : $&/eg' < $ODA_INSTALL_DIR/site/apache_odaweb.site >/tmp/onlinedisassembler.conf
sudo mv /tmp/onlinedisassembler.conf /etc/apache2/sites-available/

#need to a2ensite
sudo a2ensite onlinedisassembler
sudo service apache2 reload

}




