#!/bin/bash
#
# NOTE: Run this *before* running './manage syncdb'
# 
# The purpose of this script is to extract the user accounts from the database
# on www.onlinedisassembler.com and insert them into the new database on the new
# server (on which this script runs).
USER=`whoami`

# extract tables
ssh $USER@www.onlinedisassembler.com mysqldump --password=password --user=root odapython2 auth_user account_emailconfirmation account_emailaddress socialaccount_socialaccount socialaccount_socialapp socialaccount_socialapp_sites socialaccount_socialtoken > user_tables.sql

# import them on this server
mysql --password=password --user=root -D odapython3 < user_tables.sql
