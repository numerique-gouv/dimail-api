#!/bin/sh
NAME=$1

if [ -f /tmp/dimail_${NAME}_id_rsa -o -f /tmp/dimail_${NAME}_id_ras.pub ]; then
	rm -f /tmp/dimail_api_test_id_rsa /tmp/dimail_api_test_id_rsa.pub
fi

ssh-keygen -t rsa -b 4096 -q -N "" \
  -f /tmp/dimail_${NAME}_id_rsa \
  -C "tu@dimail"

cat /tmp/dimail_${NAME}_id_rsa.pub > ../${NAME}/authorized_keys2

