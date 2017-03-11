This repository contains scripts and configuration files for
automating system installations.

2017, Georg Sauthoff <mail@gms.tf>

## Content

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

See also the README.md files in the subdirectories.

[f]: https://en.wikipedia.org/wiki/Fedora_(operating_system)
