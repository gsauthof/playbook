This directory contains an Ansible playbook that uses a Fedora
initramfs image (as produced by mkrescuenet.py in the parent
directory) to remotely replace an existing Linux system with a
fresh Fedora installation on top of a newly created LUKS
encrypted device.

2020, Georg Sauthoff <mail@gms.tf>

## Examples

Basic usage on Digital Ocean (i.e. also creates a new droplet):

    export DO_API_TOKEN=...
    ansible-playbook kexec-boot-install.yml

Using it against some other remote system that is already running:

    echo 'create a inventory with the IP address of the remote system: '
    echo -e '[do]\n203.0.113.23' > hosts
    ansible-playbook kexec-boot-install.yml --skip-tags droplet_play \
            -i hosts -e ssh_key_name='myclientkeyprefix'

Getting started with Linode:

    echo 'Upload ssh-host-key-stackscript.sh to your Linode StackScripts'
    echo 'or just use gsauthof/ssh-host-key (id: 660652)'
    echo 'adjust ./mk-linode.sh'
    ./mk-linode.sh
    echo 'continue with previous example'

OCD usage (replace the host key one more time ...):

    rm -rf work
    ansible-playbook kexec-boot-install.yml ...
    < work/pw ssh root@203.0.113.23 systemd-tty-ask-password-agent
    rm work/*key*
    ansible-playbook kexec-boot-install.yml --tags keys_play,hostkey_play -i hosts
    ssh root@203.0.113.23 dracut -f


## Troubleshooting

By default, and for good reason, the initramfs image has the root
account locked - i.e. only public-key authentication is possible.
For debugging purposes a login on the console might be useful. In
such cases the root account can be unlocked via an additional
sideload.

For example, by adding something like this to the `create
sideload` task:

    mkdir etc/rc.d
    echo -e '#!/bin/bash\necho root:some-newly-gen-pw | chpasswd' > etc/rc.d/rc.local
    chmod 755 etc/rc.d/rc.local


## Tested VM Providers

Some notable VM providers where this playbook was tested:

- DigitalOcean
- Hetzner
- Linode

