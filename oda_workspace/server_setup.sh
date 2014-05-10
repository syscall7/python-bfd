These are rough notes, and you must not mindlessly follow them.

# Upgrade the server
sudo apt-get update
sudo apt-get upgrade

# Install subversion
sudo apt-get install subversion

# Build BFD library
sudo apt-get install texinfo
sudo apt-get install patch
sudo apt-get install bzip2
sudo apt-get install gcc make autoconf
cd ~
svn co svn://svn.onlinedisassembler.com/oda/ODA/trunk/bfd
cd bfd
sudo ./build_bfd.sh

# Setup apache and mysql
sudo apt-get install apache2 libapache2-mod-wsgi mysql-server libmysqlclient-dev
sudo usermod -aG www-data anthony

# Setup the python environment
sudo apt-get install python-pip
sudo apt-get install python-virtualenv
sudo mkdir /var/www/oda2
sudo chown www-data /var/www/oda2
sudo chgrp www-data /var/www/oda2
sudo virtualenv /var/www/oda2/env
sudo chown -R www-data /var/www/oda2/env/
sudo chgrp -R www-data /var/www/oda2/env/
sudo apt-get install libffi-dev # for gsutil
sudo /var/www/oda2/env/bin/pip install -r requirements.txt

# Build BFD module
cd ~/bfd
sudo apt-get install python-dev cython
sudo /var/www/oda2/env/bin/python setup.py install

# Create database
mysql -u root -p
create database odapython2;
exit;

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

# TODO: Add notes about setting up ssl
copy default-ssl from server
a2enmod ssl
sudo service apache2 reload

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

# Setup mail
create sendgrid account (Anthony has one to use)

