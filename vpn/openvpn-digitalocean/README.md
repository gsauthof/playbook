This directory contains a [Vagrant][vagrant] playbook that
creates a [DigitalOcean][do] machine ('droplet') running a fully
configured [OpenVPN][ovpn] endpoint in 10 minutes.

Common use cases for such a VPN are being able to work in an
unreliable and/or insecure (wireless) network, get a well-known
IP-address with proper reverse DNS records and work around silly
[geo-blocking][geo] restrictions of content providers (like video
streaming and video portals).

Since the setup of a complete virtual machine from scratch is so
quick and DigitalOcean [bills by the hour][dop] ($ 0.007
per hour, for a suitable configuration, as of 2018-02), it's convenient to
create/destroy the OpenVPN endpoint on the fly. Say - when the
VPN access is only needed in the evening, at the weekend, during
holidays or something like that.

2017, Georg Sauthoff <mail@gms.tf>

## Getting Started

After copying the necessary certificates and keys to `etc/openvpn` it's just:

    $ export do_token=my_digital_ocean_API_token
    $ export do_hostname=porta.example.org # recommended
    $ export do_region=nyc3 # optional
    $ ssh-keygen -t rsa -f ~/.ssh/do-2018-rsa -N '' < /dev/null
    $ vagrant up --provider=digital_ocean
    $ ./update_dns.py
    $ vagrant ssh -- shutdown -r now

Or  just:

    $ export do_token=my_digital_ocean_API_token
    $ export do_hostname=porta.example.org
    $ ssh-keygen -t rsa -f ~/.ssh/do-2018-rsa -N '' < /dev/null
    $ ./up.sh

Destroy the endpoint (and save some money):

    $ vagrant destroy

## Creating Certificates

One need to put the following files into `etc/openvpn` before
executing `vagrant up`:

- `ca.crt` - the certificate authority's public key (used to
  verify client certificates)
- `server.crt` - the server's public key (signed by the CA's
  private key)
- `server.key` - the server's private key
- `ta.key` - TLS auth pre-shared secret

If not already available, they can easily be generated with the
[easy-rsa][easy-rsa] package - see `mk_keys.sh` for details:

    $ sudo dnf -y install easy-rsa
    $ ./mk_keys.sh

## Android Client

The official OpenVPN client for Android is [OpenVPN
Connect][android-con]. It generally works pretty good and uses
the standard Android VPN API, such that the device doesn't have
to be rooted. But it is closed source.

[OpenVPN for Android][android-open] is an alternative
**Open-Source** client that also uses the standard Android VPN
API. Besides being open-source, it also provides some bonus
features, e.g. enabling VPN only for selected apps or excluding
some apps from the VPN.

In the experience of the author of these lines, OpenVPN for
Android is less reliable, though, e.g. in preventing leaks (as of
2018-01).

The simplest way to getting started under Android is to import a
`.ovpn` profile file. Both Android OpenVPN client support this.

Example:

   $ ./mk_ovpn $do_hostname > my.ovpn


## DNS

DigitalOcean (conveniently) automatically sets up a reverse DNS
record if the droplet name is a fully qualified hostname (cf.
the `do_hostname` environment variable in the `Vagrantfile`).

For keeping the client setup simple it makes sense to use a fully
qualified hostname. The necessary domain doesn't have to be
expensive, standard domain registrars charge 5 Euros per year or so
for a standard domain.

Some domain registrars also act as domain name server providers,
by default, without extra charge. And some even include a [dynamic
DNS][ddns] API (e.g. INWX, as beta service, as of 2018-02).

There is also [he.net][he] who (beside other great services) also
provide a free-tier name server service (for up to 50 domains, as
of 2018-02) that includes a dynamic DNS API.

See `update_dns.py` for how to update DNS records using an API:

    $ ./update_dns.py


## Discussion

The droplet and the OpenVPN server is also reachable via IPv6,
but the actual VPN is currently IPv4 only.

Working around [geo-blocking][geo] isn't always that simple. For
example, Netflix: using a VPN endpoint in the DigitalOcean New
York datacenter only worked until 2016; when [Netflix announced to
invest into some more sophisticated geo-blocking][tf]. As of 2018-02,
Netflix doesn't work out of the DigitalOcean New York and Toronto
datacenters. Since it's straight forward to look up the
IP-address ranges VM-providers like DigitialOcean are using,
Netflix likely does that and blocks those ranges.

Other content providers don't necessarily are as motivated in
blocking VPNs as Netflix. The author of this README is aware of
another nice streaming provider that doesn't block DigitalOcean.
Also, Youtube should work, too.

Although the created droplet is primarily used as OpenVPN
endpoint, it installs some good default dot-files in case one has
to ssh into it.

The startup procedure also contains a reboot step because the
standard DigitalOcean CentOS image isn't update'd between
releases such that the first package update likely requires a
reboot.

The setup script also enables auto-updates for yum, thus, in case
the droplet is online for an extended time period it has to be
rebooted - from time to time (as reboot-requiring updates like a
kernel update likely happen - from time to time).

The `update_dns.py` script uses the HTTPS GET `nic/update?myip=`
style dynamic DNS update 'protocol' that it supported in some
variation by many DNS providers. One known difference is how
providers expect IPv6 address updates. For example, INWX supports
the additional `myipv6` parameter, while he.net auto-detects IPv6
addresses and thus expects 2 separate GET requests. The script
just does HTTPS for obvious security reasons and authentication
happens via basic auth.

## Files

- `dns-sample.json` - example of a `dns.json` config file that
   is read by `update_dns.py`
- `etc/` - configuration files used during droplet provisioning
- `mk_keys.sh` - generates client/server/ca keys using
  easy-rsa and copies the files needed by the server to `etc/`
- `mk_ovpn.sh` - creates `.ovpn` profile files based on the keys
  generated previously by `mk_keys.sh`
- `netrc-sample` - example configuration of credentials used by
  `update_dns.py`
- `setup.sh` - provision script that turns a vanilla CentOS 7
  system into a fully configured OpenVPN endpoint
- `update_dns.py` - update DNS entries via dynamic DNS API calls,
  requires the `dns.json` and `netrc` configuration files
- `up.sh` - provisions the OpenVPN endpoint from scratch
  (including DNS updates) after
  checking for the necessary environment variables
- `Vagrantfile` - [Vagrant][vagrant] configuration file, commands
  like `vagrant up` look for it in the current working directory

[easy-rsa]: https://github.com/OpenVPN/easy-rsa
[vagrant]: https://en.wikipedia.org/wiki/Vagrant_(software)
[do]: https://en.wikipedia.org/wiki/DigitalOcean
[dop]: https://www.digitalocean.com/pricing/
[openvpn]: https://en.wikipedia.org/wiki/OpenVPN
[geo]: https://en.wikipedia.org/wiki/Geo-blocking
[ddns]: https://en.wikipedia.org/wiki/Dynamic_DNS
[he]: https://dns.he.net/
[tf]: https://torrentfreak.com/netflix-vpn-blockade-backlash-doesnt-hurt-us-190416/
[android-con]: https://play.google.com/store/apps/details?id=net.openvpn.openvpn
[android-open]: https://play.google.com/store/apps/details?id=de.blinkt.openvpn
