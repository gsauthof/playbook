#!/bin/bash


set -eux

# HWE = Hardware Enablement Kernel


# some basic packages necessary for installing grub, for booting
# or which are too useful in general
apt-get -y install \
    apt-file \
    debconf-utils \
    grub-efi-amd64 \
    keyutils \
    linux-generic \
    linux-generic-hwe-20.04 \
    linux-headers-generic \
    linux-headers-generic-hwe-20.04 \
    restic \
    vim

# the signed grub doesn't support writing to 2 ESPs ...
# cf. https://bugs.launchpad.net/ubuntu/+source/grub-installer/+bug/1466150/comments/41
apt-get -y remove grub-efi-amd64-signed


