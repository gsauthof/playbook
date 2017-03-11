#!/bin/bash

# 2017, Georg Sauthoff <mail@gms.tf>

set -eux

hostname=f25-rescue.example.org
pubkey="$HOME"/.ssh/vm-ed25519.pub
pwfile=/path/to/rootpw
dev=/path/to/dev/sdb/or/file/img
vflags=""

# overwrite above variables
. config-local.sh

virt-builder fedora-25 \
    --hostname "$hostname" \
    --ssh-inject root:file:"$pubkey" \
    --root-password file:"$pwfile" \
    --update \
    --install $(paste -d, -s package.list) \
    --run guest-setup.sh \
    --selinux-relabel \
    $vflags \
    -o "$dev"

cat <<EOF
Created rescue system in $dev successfully.

Test it with e.g.:

qemu-system-x86_64 -enable-kvm -drive file=$dev,if=virtio,format=raw -m 2048 -netdev bridge,id=nd0,name=tap0,br=virbr0 -device e1000,netdev=nd0,id=d0  -display curses

EOF

# for testing the setup script with an existing image:
#virt-customize --add "$dev" \
#    --run guest-setup.sh \
#    --selinux-relabel

