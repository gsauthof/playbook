Scripts for installing [Fedora][f] 25 to a raw disk using
[`virt-builder`][virtb] and applying a default configuration
suitable for console work like preparing a system for
installation or rescuing data.

The build script is thus well suited for preparing a bootable
Live-USB stick that can be used as a substitute for special
purpose rescue distributions like Grml. In contrast to
traditional Live systems it can be used like a normal Linux
system (e.g. `/` isn't read-only and union mounted with a ramdisk,
but normal read/write root and home filesystem).

It uses `virt-builder` because it is very fast - modulo slow USB
write speeds and slow internet access.

2017, Georg Sauthoff <mail@gms.tf>


## Example

    # chmod juser /dev/sdz
    $ cat > config-local.sh 
    hostname=f25-rescue.example.org
    pubkey="$HOME"/.ssh/my_key_ed25519.pub
    pwfile=rootpw
    dev=/dev/sdz
    $ ./build.sh
    [..]
    [1434.2] Finishing off
		       Output file: /dev/sdz
		       Output size: 14.5G
		     Output format: raw
		Total usable space: 12.9G
			Free space: 10.5G (81%)
    + cat
    Created rescue system in /dev/sdz successfully.

    Test it with e.g.:

    qemu-system-x86_64 -enable-kvm -drive file=/dev/sdz,if=virtio,format=raw -m 2048 -netdev bridge,id=nd0,name=tap0,br=virbr0 -device e1000,netdev=nd0,id=d0  -display curses


## Hardware

I tested it with a 16 GB Sandisk Ultra Fit USB 3 stick which is a
medium performance and low cost USB mass storage device (as of
2017). In my experience, it performs well enough for the
described use cases.

## Dependencies

The build script needs `virt-builder` from [libguestfs][guestfs]
- including [XFS][xfs] support.

For example, on a Fedora system:

    # dnf install libguestfs-tools libguestfs-xfs

The used virt-builder enforces a minimal target image/device size
of 6 GB - with Fedora 25 images.

As of early 2017 (Linux 4.9), writing a disk image to a
relatively slow USB stick might trigger some disk bufferbloat
symptoms - with the kernel defaults. Thus, it is a good idea to
[apply more sane settings][bloat].

## Comparison

[Grml][grml] is a great live system for system administration
tasks. Unfortunately, as of 2017, the latest stable Grml image
was released 2014. In contrast to a boot image generated with
this `build.sh`, Grml is based on Debian and it is
distributed as hybrid ISO image, i.e. it is bootable when written
to a CD but also when dumped to a USB stick. It is a classic Live
system, i.e. the software selection is restricted to fit on a CD.
Also, the filesystem is union mounted, i.e.  filesystem changes
aren't retained between boots. Nowadays perhaps less relevant,
but still interesting - there is also a (larger) variant that
both includes a 32 and 64 Bit version of the live system (named
Grml96) , i.e. one can multi-boot into 32 or 64 Bit Debian via
the bootloader. 

On the other hand, an image produced by `build.sh` is based on
the latest stable x86-64 Fedora with very current software and
Linux Kernel. It pretty much behaves like a standard Linux
system, e.g. the bootloader is the default Grub2 (not
[ISOLINUX][isolinux]), the root/home filesystem is normally
mounted, i.e. read/write, such that changes are retained between
boots. The generation of the image can easily be customized.

Since it uses Grub2, it needs a BIOS that supports booting from a
USB mass storage device (i.e. as if it were a harddisk).
Basically every BIOS shipped after 2002 or so should be
sufficient.

## Outlook

Currently, the build script uses the Fedora base image that is
distributed by the [libguestfs][guestfs] team. This image uses
[XFS][xfs] for the root file system. In practice this works good
enough - but perhaps it is beneficial to use a copy-on-write
(COW) filesystem like [Btrfs][btrfs] on USB flash drives.

There is an optimization opportunity to create the
filesystems with parameters optimized for USB flash drives (cf.
[pages, erase blocks and segments][lwnflash]). It has to be shown
whether such tuning still makes sense with current flash device
firmware, though. The default performance arguably is good
enough.

Another feature to look into is the creation of encrypted
filesystems. For example, to protect data in case the USB stick
is lost. Currently, `virt-builder` [doesn't support
encryption][vbcrypt].


[lwnflash]: https://lwn.net/Articles/428584/
[virtb]: http://libguestfs.org/virt-builder.1.html
[guestfs]: http://libguestfs.org/
[xfs]: https://en.wikipedia.org/wiki/XFS
[btrfs]: https://en.wikipedia.org/wiki/Btrfs
[f]: https://en.wikipedia.org/wiki/Fedora_(operating_system)
[bloat]: https://twitter.com/golfmikesierra/status/832336430676504577
[grml]: https://grml.org/
[isolinux]: http://www.syslinux.org/wiki/index.php?title=ISOLINUX
[vbcrypt]: https://bugzilla.redhat.com/show_bug.cgi?id=1400332
