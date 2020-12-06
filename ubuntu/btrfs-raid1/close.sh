#!/bin/bash

set -ux

# XXX Adjust below device names!
a=nvme0n1
ap="$a"p
b=sda
bp="$b"


for i in /dev/pts /dev /sys/firmware/efi/efivars /sys /proc /boot/eficopy /boot/efi /boot /home / ; do
    umount  /mnt/root$i
done

for i in 0 1; do
    cryptsetup luksClose crypt_root_$i
done
