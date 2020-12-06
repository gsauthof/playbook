In contrast to Fedora, installing Ubuntu 20.04 on an encrypted
RAID-1 mirrored root filesystem isn't supported by the default
GUI installer.

One approach is then to create the partitions and filesystems
before starting the installer, start the installer with special
options from a Ubuntu Installer Live session and finally chroot
into the new system to fix configuration and install grub.

This directory contains scripts to automate some steps:

- `setup-disks.sh` - set up partitions and create filesystems for
  the new target Ubuntu 20.04 system, i.e. Btrfs RAID-1 root
  filesystem on LUKS-encrypted devices
- `open.sh` - unlock/(bind-)mount all partitions/filesystems on a
  rescue system and make everyting ready for a `chroot /mnt/root
  bash`
- `close.sh` - reverse the effects of `open.sh`
- `setup-etc.sh` - create `/etc/fstab`, `/etc/crypttab` etc.
- `install-pkgs.sh` - install basic packages that aren't
  installed by the default installer
- `config-grub.sh` - configure and install grub


## Workflow

Basically it's:

1. Boot into the default Ubuntu 20.04 Live Installer system (i.e.
   select 'Try Ubuntu')
2. Adjust and execute `setup-disks.sh`
3. Execute Ubuntu's default installer but skip the bootloader
   installation:  `ubiquity --no-bootloader`. Select there
   'Something Else' as 'installation type' and then select the
   existing partitions LUKS devices, deselect disturbing stuff
   and make sure do have 'format' options deslected.
4. After Ubiquity is finished, unmount remaining target
   filesystems/lock partitions.
5. Execute `open.sh` before chrooting
6. Adjust and execute `setup-etc.sh`
7. Enter the chroot and execute `install-pkgs.sh` and
   `config-grub.sh`
8. Leave the chroot and unmount everything with `close.sh`


The last steps can also be executed from any other rescue system.
It doesn't have to be the Ubuntu Live system.


## Related Work


- Blog article: [Ubuntu 20.04 with btrfs-luks-RAID1 full disk encryption
  including /boot and auto-apt snapshots with Timeshift][1]



[1]: https://mutschler.eu/linux/install-guides/ubuntu-btrfs-raid1/
