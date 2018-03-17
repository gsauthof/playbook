Python program that [bootstraps][1] a [Fedora][f] system from
scratch in 2 stages.

Stage 0 works on raw devices and installs a bootable base system.
As part of that process it automatically partitions the devices,
creates the filesystems, installs the base systems, applies some
configurations (e.g. disabling password authentication in sshd)
etc. It assumes a host system where [dnf][dnf] is available (e.g.
a rescue system). For example, it uses the [Dnf
installroot][installroot] feature. Some tasks are executed in a
[chroot][chroot] environment.

Stage 1 runs inside the target system and applies typical
post-install tasks like enabling additional repositories,
installing a good default package selection, applying some sane
defaults, etc. Changes to configuration files under `/etc` are
tracked in a [Git][git] repository.

For more details on the different stages see also the `stage0`
and `stage1` functions in `configure.py` and take a look at the
example configuration file.

## Examples

Stage 0:

    # ./configure.py --log --stage=0
       0.0 DBG  Calling: 'rpm' '-E%fedora'
       0.0 DBG  Calling: 'setenforce' '0'
       0.0 INF  Running create_partitions
       0.0 DBG  Calling: 'sfdisk' '--list' '/dev/vdb'
       0.0 DBG  Calling: echo -ne 'size=1GiB, type=83, bootable\ntype=83\n' | 'sfdisk' '/dev/vdb'
       0.7 DBG  Storing state as cnf.state
       0.7 INF  Running mk_fs
       0.7 DBG  Calling: 'mkfs.ext4' '-U' 'a4733703-f855-471e-a1dd-d7d6814c12da' '/dev/vdb1'
       1.3 DBG  Calling: echo -ne '<secret>' | 'cryptsetup' 'luksFormat' '/dev/vdb2' '--key-file' '-' '--uuid' 'c44b166f-25c3-4c37-b822-8ac8340475c1'
       5.5 DBG  Calling: echo -ne '<secret>' | 'cryptsetup' 'luksOpen' '/dev/vdb2' 'new-root' '--key-file' '-'
       7.8 DBG  Calling: 'mkfs.btrfs' '--uuid' 'e9485450-56f2-4c74-b8b9-bb56e22a50fc' '/dev/mapper/new-root'
       8.0 DBG  Calling: 'mount' '-o' 'noatime' '/dev/mapper/new-root' '/mnt/new-root'
       8.1 DBG  Calling: 'btrfs' 'subvolume' 'create' '/mnt/new-root/root'
       8.1 DBG  Calling: 'btrfs' 'subvolume' 'create' '/mnt/new-root/home'
       8.2 DBG  Calling: 'umount' '/mnt/new-root'
       8.2 DBG  Calling: 'cryptsetup' 'luksClose' 'new-root'
       8.3 DBG  Storing state as cnf.state
    [..]
     585.8 DBG  Calling: 'chroot' '/mnt/new-root' 'useradd' '--groups' 'wheel' '--create-home' 'juser'
     586.1 DBG  Storing state as cnf.state
     586.1 INF  Running set_user_password
    [..]
     594.1 DBG  Calling: 'cryptsetup' 'luksClose' 'new-root'
     594.2 DBG  Storing state as cnf.state

Stage 1:

    # ./configure.py --log --stage 1
       0.0 INF  Started at 2017-07-09 18:12:26
       0.0 DBG  Calling: 'rpm' '-E%fedora'
       0.0 INF  Running mk_etc_mirror
       0.0 DBG  Calling: 'git' '--work-tree=/etc' '--git-dir=/root/etc-mirror' 'init'
       0.0 DBG  Calling: 'git' '--git-dir=/root/etc-mirror' 'config' 'user.email' 'juser@example.org'
       0.0 DBG  Calling: 'git' '--git-dir=/root/etc-mirror' 'config' 'user.name' 'Joe User'
       0.1 DBG  Storing state as cnf.state
       0.1 INF  Running commit_core_files
       0.1 DBG  Calling: 'git' '--git-dir=/root/etc-mirror' 'add' 'crypttab' 'fstab' 'default/grub'
       0.1 DBG  Calling: 'git' '--git-dir=/root/etc-mirror' 'commit' '-m' 'add core etc files'
       0.1 DBG  Storing state as cnf.state
       0.1 INF  Running add_rpmfusion
       0.1 DBG  Calling: 'curl' '-f' '-L' '-o' './RPM-GPG-KEY-rpmfusion-free-fedora-26' 'https://rpmfusion.org/keys?action=AttachFile&do=get&target=RPM-GPG-KEY-rpmfusion-free-fedora-26'
       0.5 DBG  Calling: 'gpg2' '--with-fingerprint' './RPM-GPG-KEY-rpmfusion-free-fedora-26'
       0.5 DBG  Calling: 'rpm' '--import' './RPM-GPG-KEY-rpmfusion-free-fedora-26'
       0.7 DBG  Calling: 'curl' '-f' '-L' '-o' './rpmfusion-free-release-26.noarch.rpm' 'https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-26.noarch.rpm'
       1.2 DBG  Calling: 'rpm' '--checksig' './rpmfusion-free-release-26.noarch.rpm'
       1.2 DBG  Calling: 'dnf' '-y' 'install' './rpmfusion-free-release-26.noarch.rpm'
       [..]
       3.4 DBG  Calling: 'git' '--git-dir=/root/etc-mirror' 'commit' '-m' 'add rpmfusion repo'
       3.4 DBG  Storing state as cnf.state
       3.4 INF  Running add_livna
       3.5 DBG  Calling: 'curl' '-f' '-L' '-o' './livna-release.rpm' 'http://rpm.livna.org/livna-release.rpm'
       [the script checks the sha256 hash of the download ...]
       5.1 DBG  Calling: 'dnf' '-y' 'install' './livna-release.rpm'
      11.7 DBG  Calling: 'git' '--git-dir=/root/etc-mirror' 'add' 'pki/rpm-gpg/RPM-GPG-KEY-livna' 'yum.repos.d/livna.repo'
      11.8 DBG  Calling: 'git' '--git-dir=/root/etc-mirror' 'commit' '-m' 'add livna repo'
      11.8 DBG  Storing state as cnf.state
      11.8 INF  Running set_host
      11.8 DBG  Calling: 'git' '--git-dir=/root/etc-mirror' 'add' 'hosts'
      11.8 DBG  Calling: 'git' '--git-dir=/root/etc-mirror' 'commit' '-m' 'add hosts'
      11.8 DBG  Calling: 'hostnamectl' 'set-hostname' 'f26.example.org'
       [..]
      31.1 DBG  Calling: 'dnf' '-y' 'install' [..]
    7530.4 DBG  Calling: 'git' '--git-dir=/root/etc-mirror' 'commit' '-m' 'record users/groups created by newly installed packages'
    7530.4 DBG  Storing state as cnf.state
    7530.4 INF  Running disable_avahi
       [..]

## Quick Start

1. Boot an existing Fedora system/image where the target disks
   are attached. Either on bare metal or inside Qemu.
2. Checkout this repository.
3. Create a `system.cnf` (based on one of the examples)
4. Create a `pw` file that contains the password for the target.
5. Create a `package.list` that contains a selection of packages.
   See also this directory for examples.
6. Create a `unpackage.list` for deinstalling unwanted packages
   from the base system (cf. this directory).
6. Change to the root user.
7. Execute: `./configure --stage 0`
8. Boot into the new system
9. Execute: `./configure --stage 1` in `/root/play-$release`
   directory.

See also: `./configure.py --help`

## Notes

The configure Python program reads some configuration from
`system.cnf` and writes state information to `cnf.state`. The
state file is for [memoizing][m] the success of the different tasks.
In case one task fails, the program exits, the user can fix the
situation and then restart configure. To force the re-execution
of some tasks the state file can be edited with a text editor,
simply deleted and there is also a `--clear` command line option.

## UEFI

The stage 0 partitions the disk or disks, creates the filesystems
and installs the bootloader in a way such that the result boots
on legacy [BIOS][bios] and [UEFI][uefi] firmware systems. That
means that it implements a hybrid approach.

In detail this is achieved via:

1. Unconditionally creating [GPT partitions][gpt]. The legacy
   BIOS boot only cares about the [MBR][mbr] and not about the
   partition scheme.
   Also, GPT still leaves space for the MBR (for backwards
   compatibility). [Grub2][grub2] has no problems to read GPT
   partitions when booted via legacy BIOS.
2. Creating a [BIOS Boot Partition][bbp]. This is required when
   installing Grub2 into the MBR of a GPT. In DOS style
   partitioning Grub2 uses the space between the MBR and the
   first partition. This isn't available with GPT, thus this
   extra (tiny) partition.
3. Unconditionally installing [Grub2][grub2] into the [MBR][mbr]
   *and* into the [EFI System Partition][esp]. This works because
   UEFI-only systems ignore the MBR and Legacy boot systems just
   use the MBR.

The advantages of this hybrid approach are:

- flexibility - the system disk/disks can easily transplanted
  between UEFI and legacy boot systems
- simplicity - the same provisioning code is executed on all
  systems

## See also

Yum, the predecessor of Dnf, also has an installroot mode. Debian
has similar functionality, in the [debootstrap][debootstrap]
utility.

The official install method of Gentoo in 1999 or so was to
execute a bunch of commands in a [chroot][chroot] of a Live CD.

Using chroot for installing custom Linux systems and recovering
existing ones is a classic use case.

The blog article [Fedora from scratch][2] from 2013 describes the
experience of installing Fedora 20 with Yum's installroot
features also using a chroot for some steps. One described
gotcha, how the mapped name of the Luks volume is picked up by
dracut, certainly doesn't apply to Fedora 26.


[dnf]: http://dnf.readthedocs.io/en/latest/
[chroot]: https://en.wikipedia.org/wiki/Chroot
[installroot]: http://dnf.readthedocs.io/en/latest/command_ref.html#installroot-label
[debootstrap]: https://wiki.debian.org/Debootstrap
[m]: https://en.wikipedia.org/wiki/Memoization
[1]: https://en.wikipedia.org/wiki/Bootstrapping
[f]: https://en.wikipedia.org/wiki/Fedora_(operating_system)
[git]: https://en.wikipedia.org/wiki/Git
[2]: https://www.djc.id.au/blog/fedora-from-scratch
[gpt]: https://en.wikipedia.org/wiki/GUID_Partition_Table
[esp]: https://en.wikipedia.org/wiki/EFI_system_partition
[bbp]: https://en.wikipedia.org/wiki/BIOS_boot_partition
[uefi]: https://en.wikipedia.org/wiki/Unified_Extensible_Firmware_Interface
[bios]: https://en.wikipedia.org/wiki/BIOS
[mbr]: https://en.wikipedia.org/wiki/Master_boot_record
[grub2]: https://en.wikipedia.org/wiki/GNU_GRUB#Version_2_(GRUB)
