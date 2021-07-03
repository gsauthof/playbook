This directory contains a set of [Ansible][ansible] playbooks and
roles for setting up servers.

Depending on the purpose of the target server, only a subset of
these roles is appropriate.

The roles target Fedora systems, but should be generic enough to also
work on not too old RHEL/CentOS ones. Or even on other Linux distributions
to some degree, perhaps requiring some adjustment.

All roles expect that the target system has SELinux and firewalld
enabled which is also the default on Fedora/RHEL/CentOS. Thus,
most roles also contain some tasks to deal with
SELinux/Fireralld, e.g. fixing some labeling, adjusting related
configuration/policies, etc.

2021, Georg Sauthoff <mail@gms.tf>

## Roles

- basic - basic setup such as installing commonly needed
  packages, securing the sshd etc.
- root - set up the root user, i.e. a good shell, dotfiles etc.
- user - set up the main non-root user, i.e. add authorized key,
  set a good shell etc.
- dracut-sshd - set up [dracut-sshd][dsd] in order to connect to
  the early boot environment for unlocking encrypted disks or
  troubleshooting
- matrix-client - set up a [matrix][mtx] client for some system
  notifications
- restic - set up system wide backup, e.g. to Backblaze B2 object
  storage
- wireguard - set up a [WireGuard][wg] tunnel between two hosts (i.e.
  'buddies'), i.e. including creating public/private key-pairs on
  each remote host and distributing the public keys
- postgres - set up [postgres][pg] with [SCRAM][scram] authentication and
  logical replication (over a WireGuard tunnel)
- web - set up Nginx for some domains, enable TLS, tune some
  settings and enroll into [Let's Encrypt][le]. Getting proper
  TLS certificates requires a small dance, e.g. starting with
  self-signed certificates to get the Nginx going, calling the
  certbot with a bunch of options, restarting Nginx multiple
  times etc. The role also takes care of establishing some sane
  directory structure for certificate, running certboot under
  a non-root technical user, adjusting permissions and SELinux
  settings.
- radicale - set up the [Radicale][rc] CalDAV/CardDAV server
  behind nginx
- syncthing - set up [SyncThing][st] for the main user



2021, Georg Sauthoff <mail@gms.tf>

[ansible]: https://en.wikipedia.org/wiki/Ansible_(software)
[dsd]: https://github.com/gsauthof/dracut-sshd
[mtx]: https://en.wikipedia.org/wiki/Matrix_(protocol)
[wg]: https://en.wikipedia.org/wiki/WireGuard
[scram]: https://en.wikipedia.org/wiki/Salted_Challenge_Response_Authentication_Mechanism
[pg]: https://en.wikipedia.org/wiki/PostgreSQL
[le]: https://en.wikipedia.org/wiki/Let%27s_Encrypt
[rc]: https://radicale.org
[st]: https://en.wikipedia.org/wiki/Syncthing
