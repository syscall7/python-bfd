sudo apt-get install python-pip
sudo pip install virtualenv
sudo apt-get install python-pip libmysqlclient-dev libffi-dev libpython-dev libssl-dev

virtualenv oda
source oda/bin/activate
pip install -r requirements.txt