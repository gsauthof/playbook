This repository contains scripts and configuration files for
automating system installations.

2017, Georg Sauthoff <mail@gms.tf>

## Content

- `android` - snippets and Android app id lists for getting
  started with a fresh Android device. That means for
  semi-automatically installing a bunch of apps from the
  google and/or the f-droid store.

- `chromium` - a selection of essential Chrome extensions

- `fedora/rescue-stick` - scripts that install [Fedora][f] on a raw
  disk, e.g. on a USB mass storage device, with a configuration
  suitable for system administration tasks (think: repairing a
  broken system, rescuing data, initiating installations,
  diagnosing network issues, ...). Uses `virt-builder`.

- `fedora/btrfs-raid1-server` - Kickstart configuration suitable
  for server usage. Root filesystem is created as Btrfs RAID1.
  The actual kickstart file is generated from a template and
  contains a non-trivial post-section for applying some
  useful defaults.

- `fedora/workstation` - a good default package selection
  for a development workstation (~500 packages).
  (TODO: add some setup and configuration files)

- `firefox` - a good default list of addons for [Firefox][ff] and
  [Firefox on Android][ffa]. Some of the addons simplify
  development tasks, some increase the convenience of daily
  browsing and the remaining ones are just indispensable.

See also the README.md files in the subdirectories.

[f]: https://en.wikipedia.org/wiki/Fedora_(operating_system)
[ff]: https://en.wikipedia.org/wiki/Firefox
[ffa]: https://play.google.com/store/apps/details?id=org.mozilla.firefox
