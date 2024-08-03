#!/bin/sh
rm -f /tmp/dimail_api_test_id_rsa /tmp/dimail_api_test_id_rsa.pub

ssh-keygen -t rsa -b 4096 -q -N "" \
  -f /tmp/dimail_api_test_id_rsa \
  -C "tu@dimail"

cat /tmp/dimail_api_test_id_rsa.pub > ../dktest/authorized_keys2

