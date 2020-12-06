#!/bin/bash

set -eux

# XXX Adjust below device names!
a=nvme0n1
ap="$a"p
b=sda
bp="$b"


i=0
for disk in $ap $bp ; do
    cryptsetup luksOpen /dev/"$disk"4 crypt_root_$i
    i=$((i+1))
done


mkdir -p /mnt/root

mount -o noatime,subvol=@ /dev/mapper/crypt_root_0 /mnt/root
mount -o noatime,subvol=@home /dev/mapper/crypt_root_0 /mnt/root/home
mount -o noatime /dev/"$ap"3 /mnt/root/boot

mount -o noatime /dev/"$ap"2 /mnt/root/boot/efi

mkdir -p /mnt/root/boot/eficopy
mount -o noatime /dev/"$bp"2 /mnt/root/boot/eficopy

for i in /dev /dev/pts /sys /sys/firmware/efi/efivars /proc; do
    mount --bind $i /mnt/root$i
done

cp /etc/resolv.conf /mnt/root/etc/

# enter chroot with:
#
# chroot /mnt/root bash


