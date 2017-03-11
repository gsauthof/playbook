[Kickstart][ks] template for installing a [Fedora][f] on a
[Btrfs][btrfs] RAID1 with some default package selections and
other defaults.

## Example

    $ cp cp config-example.yaml config.yaml
    $ vim config.yaml # modify some variables
    $ make
    $ less ks.cfg # inspect the result

## Usage

The [Kickstart][ks] file [controls Anaconda][an], the default Fedora
installer. When supplied, it runs fully automatic without
any user interaction.

The [Kickstart][ks] file can be supplied in several ways, e.g.:

- injected into initrd when installing with [`virt-install`][vi]
- stored on an additional device that is labeled `OEMDRV` and
  connected at the same time anaconda starts (think: USB stick)
- referenced via a kernel parameter (and then loaded e.g. over
  the net)
- when running a rescue system: specified via a command line
  option to a manually started `anaconda`
- placed onto a remastered ISO image


### Rescue Anaconda Example

Say the target system is booted with a rescue system and
a install tree is available (e.g. via an ISO image):

    $ scp ks.cfg f25-rescue.example.org:
    $ ssh f25-rescue.example.org
    # mkdir /mnt/cdrom
    # losetup -r -f Fedora-Server-dvd-x86_64-25-1.3.iso
    # mount -o ro /dev/loop0 /mnt/cdrom
    # anaconda --kickstart ks.cfg --repo file:///mnt/cdrom

## Features

- no swap creation - RAM is cheap and nowadays installed in large
  amounts everywhere
- anti-disk-bufferbloat settings
- some useful packages installed by default
- a default selection of dotfiles

## Dependencies

The template is instantiated with [mustache][mustache]. On
Fedora, it is part of the `rubygem-mustache` package, e.g.:

    # dnf install rubygem-mustache

[vi]: https://linux.die.net/man/1/virt-install
[ks]: https://en.wikipedia.org/wiki/Kickstart_(Linux)
[btrfs]: https://en.wikipedia.org/wiki/Btrfs
[f]: https://en.wikipedia.org/wiki/Fedora_(operating_system)
[bloat]: https://twitter.com/golfmikesierra/status/832336430676504577
[an]: http://pykickstart.readthedocs.io/en/latest/
[mustache]: https://mustache.github.io/mustache.1.html

