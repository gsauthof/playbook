#!/bin/bash

# Create a new Linode instance that is ready to be re-deployed with
# kexec-boot-install.yml.
#
# This is implemented via a simple script since the Linode Ansible Module
# currently doesn't support StackScripts cf. 'Support StackScripts and
# StackScript data in Linode Module'
# https://github.com/ansible-collections/community.general/issues/723
#
# 2020, Georg Sauthoff <mail@gms.tf>

set -x

linode=foohost

# WARNING: this exposes the root password when executing below command on a
# multi-user host
# unfortunately, currently linode-cli doesn't support a more secure non-interactive way
# cf. 'Secure non-interactive ways for specifying the root password'
# https://github.com/linode/linode-cli/issues/200

# stackscript 660652 -> gsauthof/ssh-host-key

linode-cli linodes create   \
    --type g6-standard-1    \
    --region eu-central     \
    --image linode/fedora32 \
    --authorized_keys "$(cat ~/.ssh/dell12_2017_ed25519.pub)" \
    --booted true           \
    --label "$linode"       \
    --tags mail             \
    --tags web              \
    --stackscript_id 660652 \
    --stackscript_data '{ "host_key": "'"$(< work/early_ssh_host_ed25519_key | base64 -w0)"'", "host_key_pub": "'"$(< work/early_ssh_host_ed25519_key.pub | base64 -w0)"'" }' \
    --root_pass "$(cat work/pw)" \
    --swap_size 0


linode_id=$(linode-cli linodes list --label "$linode" --text --no-headers --format id)
config_id=$(inode-cli linodes configs-list "$linode" --text --no-headers --format id)


# make sure that we use our own Grub located in the MBR of the local disk
# for all following boots
linode-cli linodes config-update --kernel linode/direct-disk "$linode_id" "$config_id"

