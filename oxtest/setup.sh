#!/bin/bash

MYSQL="mysql -u root -ptoto -h mariadb"
apt-get install -y mariadb-client
res=$($MYSQL -B -N -e 'show databases like "ox_config"')
echo $res

if [ "$res" = "" ]; then
	# We need to create the database
	echo Creating main DB with initconfigdb
	/opt/open-xchange/sbin/initconfigdb \
		--configdb-host=mariadb \
		--configdb-dbname=ox_config \
		--configdb-pass=oxtoto \
		--configdb-user=ox \
		-a \
		--mysql-root-passwd=toto
	echo Done
fi

res=$(grep "SERVER_NAME=ox_test" /opt/open-xchange/etc/system.properties)

if [ "$res" = "" ]; then
	# We need to launch the OX Installer
	echo Launch OX installer
	/opt/open-xchange/sbin/oxinstaller --no-license \
		--servername=ox_test \
		--configdb-user=ox \
		--configdb-readhost=mariadb \
		--configdb-writehost=mariadb \
		--configdb-pass=oxtoto \
		--configdb-dbname=ox_config \
		--master-user=master_user \
		--master-pass=master_pass \
		--network-listener-host=localhost \
		--servermemory 2048
	echo Done
fi

nb_server=$($MYSQL -B -N -e 'SELECT COUNT(*) FROM ox_config.server;')
nb_filestore=$($MYSQL -B -N -e 'SELECT COUNT(*) FROM ox_config.filestore;')
nb_dbpool=$($MYSQL -B -N -e 'SELECT COUNT(*) FROM ox_config.db_pool;')

echo Starting OX
su -s /bin/bash open-xchange /opt/open-xchange/sbin/open-xchange&
echo Waiting 25 seconds...
for i in `seq 1 25`; do
	echo "$i "
	sleep 1
done
echo done waiting
echo Started OX

if [ "$nb_server" = "0" ]; then
	echo Registering server
	/opt/open-xchange/sbin/registerserver \
		--name ox_test \
		--adminuser master_user \
		--adminpass master_pass
	echo Done
fi

if [ "$nb_filestore" = "0" ]; then
	echo Creating and registering filestore
	mkdir -p /var/mail/filestore
	chown open-xchange:open-xchange /var/mail/filestore
	chmod 2755 /var/mail/filestore
	/opt/open-xchange/sbin/registerfilestore \
		--adminuser master_user \
		--adminpass master_pass \
		--storepath file:/var/mail/filestore \
		--storesize 500
	echo Done
fi

if [ "$nb_dbpool" = "0" ]; then
	echo Registering middleware DB
	/opt/open-xchange/sbin/registerdatabase \
		--adminuser master_user \
		--adminpass master_pass \
		--name ox_test_database \
		--dbpasswd toto \
		--hostname mariadb \
		--master true
	echo Done
fi

echo Starting ssh daemon
/usr/sbin/sshd -D
