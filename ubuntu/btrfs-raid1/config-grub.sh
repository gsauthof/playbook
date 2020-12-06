#!/bin/bash

set -eux

# to be executed from inside the chroot!

# i.e. select both ESPs there!
dpkg-reconfigure grub-efi-amd64

# this also installs grub on the ESPs for the first time


# to make sure that the latest /etc/crypttab is included
update-initramfs -c -k all
