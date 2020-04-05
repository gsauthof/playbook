This directory contains an [Ansible][ansible] playbook for
setting up a set of mail servers under CentOS/RHEL/Fedora.

A single mail server setup consists of [Postfix][postfix] (a
Mail Transport Agent - MTA), [Maildrop][maildrop] (a Mail
Delivery Agent - MDA), [Gonzofilter][gonzo] (a bayes classifying
spam filter) and [Dovecot][dovecot] (a IMAP server).

The playbook is designed to configure multiple mail server hosts,
i.e. usually two, to have a redundant mail infrastructure.

2020, Georg Sauthoff <mail@gms.tf>

## Requirements

- at least two hosts in different datacenters with static IP
  addresses (ok, if you must you can also start with just one)
- ability to create reverse DNS (PTR) records
- ability to configure DNS records for the involved domains


## Getting Started

Have a look at the example inventory file (`hosts.sample`), the
example host and group vars (`host_vars.sample/`,
`group_vars.sample/`) and create real ones under `hosts`,
`host_vars/` and `group_vars/`.

Execute the playbook in dry mode and check the output:

    ansible-playbook mailserver.yml -b --diff --check

Further useful Ansible command line options include `-l ...` and
`--tags ...`.

## Out of Scope

Setup steps not (yet?) covered by this playbook:

- [Let's Encrypt][le] Setup - the playbook expects the keys to be
  available under `/etc/letsencrypt/live/`
- [Reverse DNS][rdns] (PTR) records setup - this is just very provider
  specific and often not even accessible via an API (think: you
  may have to request PTR changes via the support)
- DNS setup - again, different nameserver hosters have different
  APIs, no common standard. And I'm not aware of an Ansible module
  that supports some common name server hosters/DNS servers.
- [Gonzofilter][gonzo] training - see the Gonzofilter
  [README][gonzo] for details.

### DNS Setup

Basically, you have to care about the following things:

- proper [MX records][mx] for additional domains your mail server should
  retrieve mail for
- [SPF records][spf]
- [reverse DNS][rdns] (PTR) records

## See Also

Even if your setup is perfect, it's a good idea to keep an eye on [blacklists][bl]. Your
mail server might end up there by mistake or because of actions by
previous owners of your domain/IP-addresses/subnet.


[spf]: https://gms.tf/configuring-spf-to-make-google-happy.html
[bl]: https://github.com/gsauthof/utility#check-dnsbl
[gonzo]: https://github.com/gsauthof/gonzofilter
[ansible]: https://en.wikipedia.org/wiki/Ansible_(software)
[postfix]: https://en.wikipedia.org/wiki/Postfix_(software)
[dovecot]: https://en.wikipedia.org/wiki/Dovecot_(software)
[maildrop]: https://en.wikipedia.org/wiki/Maildrop
[rdns]: https://en.wikipedia.org/wiki/Reverse_DNS_lookup
[mx]: https://en.wikipedia.org/wiki/MX_record
[le]: https://en.wikipedia.org/wiki/Let%27s_Encrypt
