The script `mkrescuenet.py` installs a minimal Fedora version
into an [initramfs][3] archive. This means that the created
archive (and kernel) can be used as a rescue system which can
be directly booted from a running Linux system.

Usage example: you have a system running in a remote location on
which you have root access but nothing else. That means network
boot isn't configured in the BIOS to probe a PXE boot server
(which could be instructed to temporarily provide a rescue boot
image), there is no [BMC][4] (or you don't have access to it)
where you could attach an ISO file, no remote hands which could
attach a rescue USB stick and change BIOS settings - nothing.
With an initramfs image created by `mkrescuent.py` booting into a
rescue system can be as simple as:

    $ cat f32.cpio.xz site-keys.cpio.xz > f32-rescue.cpio.xz
    # kexec -l f32.vmlinuz --initrd=f32-rescue.cpio.xz --command-line=''
    # kexec -e

The image contains a standard DHCP configuration for all network
interfaces and starts an OpenSSH server for
remote access. The `site-keys.cpio.xz` archive contains
site-specific files which are merged into the root filesystem
such as authorized SSH keys, host keys and additional
network configuration.
[Kexec][2] allows booting a new kernel from a running Linux
system.

2020, Georg Sauthoff <mail@gms.tf>

## Use Cases

Being able to boot into such a rescue system allows to e.g.:

- Change the partitioning of the main disk and/or root
  filesystem of the target system
- Install a completely different operating system which isn't
  supported by the current system's upgrade mechanism
- Encrypt or decrypt the root filesystem, i.e. move it into a
  newly created LUKS device/or away from it ([example][1])
- ...

## Image Creation

To create the main Fedora image with all the defaults:

```
# vim pw # enter root password
# ./mkrescuenet.py --pw pw
# ls
f32.cpio.xz
f32.vmlinuz
initramfs-f32
pw
```

Since the script installs packages (into a work directory) it has
to be executed as root.

To create a simple site specific archive with newly generated ssh
host keys and the specified SSH public key for authorized access:

```
$ ./mkrescuenet.py --mk-config --keys /home/juser/.ssh/fancy.pub
$ ls
config-f32
config-f32.cpio.xz
```

This command doesn't require root. However, when executed as
non-root-user it requires the `gen_init_cpio` command which is
distributed with the Linux kernel (in the `usr` subdirectory; a
copy from the linux-5.6 release is also included in this
repository).

Both images can then be simply concatenated, the Linux kernel
is able to deal with such files:

```
$ cat f32.cpio.xz config-f32.cpio.xz > f32-rescue.cpio.xz
```

Alternatively, one can add some files to a work directory and use
`mkrescuenet.py` for just the image creation:

```
# ./mkrescuenet.py --make --d config-32 -o site-load.cpio.xz
```


## Space Considerations

Depending on the exact package selection and distribution
release, the generated (compressed) initramfs image is 100 MiB to
175 MiB big.  On the one hand this is quite small for a minimal
general purpose distribution. On the other hand it's big if you
think about past rescue systems that fit on a single floppy disk.

The `mkrescuenet.py` implements some measures to keep the size
down, e.g. a small minimal set of packages, documentation isn't
installed, locales and timezones are deleted etc.

But it still includes many utilities, lots of firmware, kernel modules
and other useful stuff such that it's as big as it is.

After all, it's a trade-off.

With gigabytes of RAM being the default it's really small enough
to boot and work with. It's also tested with a 2 GiB RAM VM which
works fine.

The created system includes `microdnf` thus one can install
additional packages once the rescue system is running.


## Boot Methods

The initramfs archive and kernel created by `mkrescuenet.py` can
directly be booted with [kexec][2] (cf. the introduction) from a
running Linux system.

Alternatively, one can boot it via Grub, i.e. by adding another
entry for the generated initramfs and kernel with minimal
parameters and copy the archive and kernel to the `/boot`
partition.

With Grub, it's possible to select such a rescue entry just once
for the next boot.


## Security

The included OpenSSH server has password authentication disabled
for security reasons. Thus, it's required to side load some
authorized SSH public keys for public key authentication. See
also the above image creation example and the `--mk-config`
option.

When using `--mk-config`, new host-keys are generated for the
side load and their fingerprints are printed to the console.
Those can be stored for comparison when connecting for the first
time to detect any MITM attack.

The side load mechanism allows for much flexibility, e.g. one
doesn't have to use `--mk-config` and can instead prepare a
custom archive that includes - say - sshd configuration for CA
signed host keys.

The `--pw` option allows to set a password for the root user.
Without that option the root account is locked, meaning that
remote ssh root access is possible while console root login in the
datacenter is not.

The rescue system has SELinux disabled because its default
package selection misses the `selinux-policy` package. Having
SELinux enabled may help when rescuing an SELinux enabled system,
although it's still a tedious process as one has to take care to
run in permissive mode and load the SELinux policy of the target
system. Alternatively, one can set such a target system to
permissive mode and trigger an autorelabeling to fix any SELinux
file contexts after modifications.

## Testing

The generated image can also be tested with QEMU.

Example:

```
qemu-system-x86_64 -nographic -enable-kvm -m 2G  \
    -netdev user,hostfwd=tcp::10023-:22,id=n1 -device virtio-net,netdev=n1 \
    -device virtio-rng-pci -cpu host \
    -kernel f32.vmlinuz -initrd f32-all.cpio.xz \
    -serial mon:stdio -echr 2 -append 'console=ttyS0,115200'
```

The serial console settings allow to interact with the guest
system from the same terminal. After login, it's recommended to
fix the guest console with `resize && reset`.



[1]: https://unix.stackexchange.com/a/584275/1131
[2]: https://en.wikipedia.org/wiki/Kexec
[3]: https://en.wikipedia.org/wiki/Initial_ramdisk
[4]: https://en.wikipedia.org/wiki/Intelligent_Platform_Management_Interface#Baseboard_management_controller

