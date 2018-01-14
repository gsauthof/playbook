This repository contains scripts and configuration files for
automating system installations.

The fedora directory also showcases different approaches to
automatically installing [Fedora][f]: using [Kickstart][ks],
[virt-builder][virt], [Vagrant][v] and [Python][p]. All the
approaches deal with partitioning and typical post-installation
tasks. Some include advanced configuration choices like Btrfs
RAID-1 and encrypted root setup.

2017, Georg Sauthoff <mail@gms.tf>

## Content

- `android` - snippets and Android app id lists for getting
  started with a fresh [Android][a] device. That means for
  semi-automatically installing a bunch of apps from the
  google and/or the [F-Droid][fdroid] store.

- [`chromium`][c] - a selection of essential Chrome extensions

- `fedora/rescue-stick` - scripts that install [Fedora][f] on a raw
  disk, e.g. on a USB mass storage device, with a configuration
  suitable for system administration tasks (think: repairing a
  broken system, rescuing data, initiating installations,
  diagnosing network issues, ...). Uses [`virt-builder`][virt].

- `fedora/btrfs-raid1-server` - [Kickstart][ks] configuration suitable
  for server usage. Root filesystem is created as Btrfs RAID1.
  The actual kickstart file is generated from a template and
  contains a non-trivial post-section for applying some
  useful defaults.

- `fedora/workstation` - a good default package selection
  for a development workstation (~500 packages) and a
  Python script that bootstraps a customized Fedora from scratch.

- `fedora/vagrant-vbox` - a good starting point for quickly
  getting a Fedora Workstation instance up and running with
  [VirtualBox][vb]. Use case: get a sane work environment under
  Windows. Typical workflow: install [Cygwin][cw] (for a
  Terminal, git and vim), install Vagrant, install VirtualBox,
  execute `vagrant up` and profit.

- `firefox` - a good default list of addons for [Firefox][ff] and
  [Firefox on Android][ffa]. Some of the addons simplify
  development tasks, some increase the convenience of daily
  browsing and the remaining ones are just indispensable.

- `gnome-shell` - a selection of useful [GNOME Shell][gs] extensions

See also the README.md files in the subdirectories.

[f]: https://en.wikipedia.org/wiki/Fedora_(operating_system)
[ff]: https://en.wikipedia.org/wiki/Firefox
[ffa]: https://play.google.com/store/apps/details?id=org.mozilla.firefox
[ks]: https://en.wikipedia.org/wiki/Kickstart_(Linux)
[virt]: http://libguestfs.org/virt-builder.1.html
[p]: https://en.wikipedia.org/wiki/Python_(programming_language)
[c]: https://en.wikipedia.org/wiki/Chromium_(web_browser)
[a]: https://en.wikipedia.org/wiki/Android_(operating_system)
[fdroid]: https://en.wikipedia.org/wiki/F-Droid
[gs]: https://en.wikipedia.org/wiki/GNOME_Shell
[v]: https://en.wikipedia.org/wiki/Vagrant_(software)
[vb]: https://en.wikipedia.org/wiki/VirtualBox
[cw]: https://en.wikipedia.org/wiki/Cygwin
