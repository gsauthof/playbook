#!/bin/bash

# Setup partitions and filesystems for encrypted Btrfs RAID-1 root filesystem
# suitable for a following Ubuntu 20.04 installation.
#
# How to use this:
#
# 1. Boot default Ubuntu 20.04 install ISO
# 2. Select live-CD mode
# 3. Adjust below device names
# 4. Execute this script
# 5. Start Ubuntu installer with `ubiquity --no-bootloader`
# 6. Re-use and select the freshly created partitions/filesystems
# 7. Chroot into the installed system and install grub
#
# 2020, Georg Sauthoff <mail@gms.tf>


set -eux

# XXX Adjust below device names!
a=nvme0n1
ap="$a"p
b=sda
bp="$b"


for disk in $a $b ; do
    sfdisk --quiet --list --output device /dev/$disk | tail -n +2 | xargs -r wipefs -a
    wipefs -a /dev/$disk
    cat <<EOF | sfdisk /dev/$disk
label: gpt
size=1MiB, type=21686148-6449-6E6F-744E-656564454649
size=200MiB, type=C12A7328-F81F-11D2-BA4B-00A0C93EC93B
size=1GiB, type=0FC63DAF-8483-4772-8E79-3D69D8477DE4
type=0FC63DAF-8483-4772-8E79-3D69D8477DE4
EOF
    if [ -e /dev/"$disk"1 ]; then
        wipefs -a /dev/"$disk"{1,2,3,4}
    else
        wipefs -a /dev/"$disk"p{1,2,3,4}
    fi
done

for disk in $ap $bp ; do
    mkfs.vfat /dev/"$disk"2
done

mkfs.btrfs --mixed --data raid1 --metadata raid1 /dev/"$ap"3 /dev/"$bp"3

i=0
for disk in $ap $bp ; do
    cryptsetup luksFormat /dev/"$disk"4
    cryptsetup luksOpen /dev/"$disk"4 new-root-$i
    i=$((i+1))
done


mkfs.btrfs --data raid1 --metadata raid1 /dev/mapper/new-root-0 /dev/mapper/new-root-1

