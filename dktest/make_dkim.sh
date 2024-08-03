#!/bin/bash

selector=$1
domain=$2
dir=`mktemp -d`

cd $dir
opendkim-genkey -v -h sha256 -b 4096  --append-domain -s $selector -d $domain
ls
echo "---- FILE $selector.txt ----"
cat $selector.txt
echo "---- EOF ----"
echo "---- FILE $selector.private ----"
cat $selector.private
echo "---- EOF ----"
cd -
rm -rf $dir

