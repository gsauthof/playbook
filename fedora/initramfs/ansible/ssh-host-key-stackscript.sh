#!/bin/bash

# Deploy a trusted ssh host key with a Linode instance.
#
# Tested on Fedora 32, should work on other distributions, too.
#
# 2020-08-01, Georg Sauthoff <mail@gms.tf>

# <UDF name="host_key" label="private SSH host key, base64 encoded"  example="output of < path/to/key base64" />
# <UDF name="host_key_pub" label="public SSH host key, base64 encoded"  example="output of < path/to/key base64" />
# <UDF name="host_key_type" label="SSH host key type" oneof="dsa,ecdsa,ed25519" default="ed25519" example="ed25519" />


# apparently, default value isn't set when omitting the parameter
# with linode-cli ...
HOST_KEY_TYPE=${HOST_KEY_TYPE:-ed25519}

dest=/etc/ssh/ssh_host_"$HOST_KEY_TYPE"_key


touch "$dest"
chmod 600 "$dest"
echo "$HOST_KEY" | base64 -d > "$dest"

echo "$HOST_KEY_PUB" | base64 -d > "$dest".pub
chmod 644 "$dest".pub

systemctl restart sshd

