#!/bin/bash -x
#
# This script assumes the following:
#   1. sudo privileges to run as the www-data user
#   2. ssh keys are setup to access the ODA servers

# bail on first error
set -e

PYTHON=/var/www/oda/env/bin/python 
SETTINGS='DJANGO_SETTINGS_MODULE=oda.settings.production'

LOCAL_MYSQL_PW='***REMOVED***'
REMOTE_MYSQL_PW='password'

#
# migrate the user accounts
#
migrate_users()
{
   SERVER=$1

   USER_ACCOUNT_TABLES='auth_user account_emailconfirmation account_emailaddress socialaccount_socialaccount socialaccount_socialapp socialaccount_socialapp_sites socialaccount_socialtoken'

    # extract tables
    ssh $SERVER -o StrictHostKeyChecking=no mysqldump --password=$REMOTE_MYSQL_PW --user=root odapython2  $USER_ACCOUNT_TABLES > /tmp/user_tables.sql

    # import them on this server
    mysql --password=$LOCAL_MYSQL_PW --user=root -D odapython3 < /tmp/user_tables.sql

}

#
# migrate the odamasters
#
migrate_odamasters()
{
    SERVER=$1

    # NOTE: The 'sleep 10' here happens on the remote side, but since SSH won't
    # close itself until all connections are closed, the tunnel stays up until
    # the migration is finished.
    PORT=`shuf -i 1024-65535 -n 1`
    ssh $SERVER -4 -f -o StrictHostKeyChecking=no -o ExitOnForwardFailure=yes -L $PORT:localhost:3306 sleep 10
    sudo $SETTINGS -u www-data $PYTHON manage.py migrate 'mysql://root:'$REMOTE_MYSQL_PW'@127.0.0.1:'$PORT'/odapython2'

}


# clear out the database if it exists
mysql --user=root --password=$LOCAL_MYSQL_PW << HERE_DOC
DROP DATABASE IF EXISTS odapython3;
CREATE DATABASE odapython3;
HERE_DOC

# migrate users from the old server (we only migrate from www.onlinedisassembler.com)
migrate_users www.onlinedisassembler.com

# sync database
sudo $SETTINGS -u www-data $PYTHON manage.py syncdb 

# setup oda database
sudo $SETTINGS -u www-data $PYTHON manage.py setup_oda 

# setup open_id
sudo $SETTINGS -u www-data $PYTHON manage.py setup_openid -m prod

# migrate from old servers
migrate_odamasters www.onlinedisassembler.com
migrate_odamasters www2.onlinedisassembler.com



