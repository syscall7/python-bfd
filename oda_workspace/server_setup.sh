These are rough notes, and you must not mindlessly follow them.

Build BFD library
    sudo apt-get install texinfo
    ./build_bfd.sh 

Build BFD module
    sudo apt-get install python-dev
    sudo /var/www/oda/env/bin/pip install cython
    sudo /var/www/oda/env/bin/python setup.py install
    
sudo apt-get install apache2
sudo apt-get install libapache2-mod-wsgi
sudo apt-get install mysql-server
sudo apt-get install python-pip
sudo apt-get install python-virtualenv
sudo apt-get install subversion
cd /var/www
sudo mkdir oda
cd oda
sudo virtualenv env
source env/bin/activate
sudo env/bin/pip install Django==1.5.1
sudo apt-get install python-dev
sudo apt-get install libmysqlclient-dev
sudo ./env/bin/pip install mysql-python
sudo svn co svn://onlinedisassembler.com/oda/ODA/trunk/django webapp
export DJANGO_SETTINGS_MODULE=oda_python.settings.production
sudo wget https://github.com/pennersr/django-allauth/archive/0.14.2.zip
sudo ../../env/bin/python setup.py  install
sudo ../env/bin/pip install djangorestframework
sudo ../env/bin/pip install django_compressor
sudo ../env/bin/pip install dnspython
sudo ../env/bin/python manage.py syncdb --settings=oda_python.settings.production
sudo ../env/bin/python manage.py setup_oda --settings=oda_python.settings.production
sudo ../env/bin/python manage.py setup_openid --settings=oda_python.settings.production -m prod
sudo cp /etc/apache2/sites-available/default /etc/apache2/sites-available/onlinedisassembler.com
sudo chown -R www-data /tmp/odaweb2
sudo chgrp -R www-data /tmp/odaweb2
sudo chown -R www-data /var/www/oda2
sudo chgrp -R www-data /var/www/oda2

# for gsutil
sudo apt-get install libffi-dev
sudo pip install gsutil

# for django google storage
pip install django-google-storage

