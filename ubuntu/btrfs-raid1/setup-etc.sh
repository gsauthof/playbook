#!/bin/bash


set -eux


# XXX adjust to /mnt/root
base=test


# XXX Adjust below device names!
a=nvme0n1
ap="$a"p
b=sda
bp="$b"

root_UUID=$(blkid -o value -s UUID /dev/mapper/crypt_root_0)
boot_UUID=$(blkid -o value -s UUID /dev/"$ap"3)
efi_UUID=$(blkid -o value -s UUID /dev/"$ap"2)
efi2_UUID=$(blkid -o value -s UUID /dev/"$bp"2)


function mk_fstab {

    cat <<EOF
# /etc/fstab: static file system information.
#
# Use 'blkid' to print the universally unique identifier for a
# device; this may be used with UUID= as a more robust way to name devices
# that works even if disks are added and removed. See fstab(5).
#
EOF

    cat <<EOF | column -t
#<filesystem> <mountpoint>   <type>  <options>       <dump>  <pass>
UUID=$root_UUID /               btrfs   defaults,subvol=@ 0       1
UUID=$root_UUID /home           btrfs   defaults,subvol=@home 0       2
UUID=$boot_UUID /boot           btrfs   defaults        0       2
UUID=$efi_UUID  /boot/efi       vfat    umask=0077      0       1
UUID=$efi2_UUID  /boot/eficopy       vfat    umask=0077      0       1
EOF

}

# NB: the crypttab target (first column) has to match the current target name
# (e.g. when opening/mounting in a rescue/live environment)
# otherwise, installing inside a chroot fails ...
function mk_crypttab {
    local i=0
    for disk in $ap $bp ; do
        echo "crypt_root_$i UUID=$(blkid -o value -s UUID /dev/"$disk"4) one4all luks,discard,initramfs,keyscript=decrypt_keyctl"
	i=$((i+1))
    done
}

function mk_grub_defaults {
    cat <<EOF
GRUB_TIMEOUT=4
GRUB_RECORDFAIL_TIMEOUT=4
EOF
}


mk_fstab > $base/etc/fstab
mk_crypttab > $base/etc/crypttab
mk_grub_defaults > $base/etc/default/grub.d/btrfs-local.cfg


