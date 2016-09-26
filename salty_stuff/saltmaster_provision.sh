#!/bin/bash

HOST_IP=''
SOFTLAYER_KEY='jhabib_id'
DOMAIN_NAME='jhabib.net'
SSH_PKEY="/home/jhabib/.ssh/id_rsa"

echo 'enter a host name: '
read HOST_NAME

# echo y | sudo slcli vs create -d sjc01 --os CENTOS_LATEST --cpu 1 --memory 1024 --hostname $HOST_NAME --domain $DOMAIN_NAME --key $SOFTLAYER_KEY

while [ "$HOST_IP" = "" ];
do 
echo 'retrieving public ip'
HOST_IP=$(sudo slcli vs list --hostname $HOST_NAME --columns primary_ip --sortby primary_ip | grep .)
sleep 3
done

echo $HOST_IP

# echo 'input public ip of saltmaster'
# read HOST_IP
# echo 'enter path to ssh private key'

# echo 'attempting ssh to saltmaster @ $HOST_IP ...'
# echo yes | sudo ssh -i $SSH_PKEY root@$HOST_IP





