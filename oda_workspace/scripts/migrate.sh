#!/bin/bash
#

migrate()
{
    SERVER=$1

    #
    # Step 1: migrate the user accounts
    #
    USER_ACCOUNT_TABLES='auth_user account_emailconfirmation account_emailaddress socialaccount_socialaccount socialaccount_socialapp socialaccount_socialapp_sites socialaccount_socialtoken'

    # extract tables
    ssh $SERVER mysqldump --password=password --user=root odapython2  $USER_ACCOUNT_TABLES> user_tables.sql

    # import them on this server
    mysql --password=password --user=root -D odapython3 < user_tables.sql

    #
    # Step 2: migrate the odamasters
    # NOTE: The 'sleep 10' here happens on the remote side, but since SSH won't
    # close itself until all connections are closed, the tunnel stays up until
    # the migration is finished.
    #
    ssh -f -o ExitOnForwardFailure=yes -L 1234:localhost:3306 sleep 10
    python manage.py migrate 'mysql://root:password@127.0.0.1:1234/odapython2'

}


# clear out the database if it exists
mysql --user=root --password=password << HERE_DOC
DROP DATABASE IF EXISTS odapython3;
CREATE DATABASE odapython3;
HERE_DOC

# sync database
python manage.py syncdb 

# setup oda database
python manage.py setup_oda 

# setup open_id
python manage.py setup_openid -m prod

# migrate from old servers
migrate www.onlinedisassembler.com
migrate www2.onlinedisassembler.com



