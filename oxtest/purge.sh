#!/bin/bash

MASTER="-A master_user -P master_pass "

remove_context() {
        cid=$1
        echo Removing context $cid
        /opt/open-xchange/sbin/deletecontext $MASTER -c $cid
}

/opt/open-xchange/sbin/listcontext $MASTER | while read cid others; do
        if [ $cid != 'cid' ]; then
                remove_context $cid
        fi
done

nb_ctx=$(/opt/open-xchange/sbin/listcontext $MASTER | wc -l)
if [ "$nb_ctx" == "1" ]; then
        echo All contexts deleted
else
        echo Il y a encore du monde
        exit 1
fi
