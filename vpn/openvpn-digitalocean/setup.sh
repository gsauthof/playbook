#!/bin/bash

# 2018, Georg Sauthoff <mail@gms.tf>
# SPDX-License-Identifier: GPL-3.0-or-later

set -x

yum -y update
yum -y install epel-release
yum -y update
yum -y install openvpn iptables-services vim git zsh screen python34 yum-cron yum-utils python2-tracer youtube-dl

yum -y remove rpcbind

git config --global user.email 'juser@example.com'
git config --global user.name 'Joe User'
git_dir=--git-dir=/root/etc-mirror
git --work-tree=/etc $git_dir init
git $git_dir add /etc/passwd /etc/group /etc/shadow /etc/yum/yum-cron-hourly.conf /etc/yum/yum-cron.conf /etc/sysconfig/iptables
git $git_dir commit -m 'add vanilla files'

cp /vagrant/etc/sysconfig/iptables /etc/sysconfig/iptables
git $git_dir add /etc/sysconfig/iptables
systemctl enable iptables.service
systemctl start iptables.service

cp /vagrant/etc/sysctl.d/openvpn.conf /etc/sysctl.d/openvpn.conf
git $git_dir add /etc/sysctl.d/openvpn.conf
git $git_dir commit -m 'enable forwarding'
sysctl --load /etc/sysctl.d/openvpn.conf

cp /vagrant/etc/openvpn/* /etc/openvpn
openssl dhparam -out /etc/openvpn/dh2048.pem 2048  2> /dev/null
chmod 600 /etc/openvpn/*.key /etc/openvpn/dh2048.pem
chmod 600 /vagrant/etc/openvpn/*.key /vagrant/etc/openvpn/dh2048.pem
git $git_dir add /etc/openvpn/server.conf
git $git_dir commit -m 'add openvpn server config'

systemctl enable openvpn@server.service
systemctl start openvpn@server.service

sed -i -e 's/^ *update_messages *= *yes/update_messages = no/' -e 's/^ *download_updates *= *no/download_updates = yes/' /etc/yum/yum-cron-hourly.conf
sed -i -e 's/^ *update_messages *= *yes/update_messages = no/' -e 's/^ *download_updates *= *yes/download_updates = no/' /etc/yum/yum-cron.conf
git $git_dir add /etc/yum/yum-cron-hourly.conf /etc/yum/yum-cron.conf
git $git_dir commit -m 'enable auto update'

git clone --quiet https://github.com/gsauthof/user-config.git ~/config
cd ~/config
git submodule update --init
./install.sh

sudo -u centos -i <<EOF
git clone --quiet https://github.com/gsauthof/user-config.git config
cd config
git submodule --quiet update --init
./install.sh
cd ..
git clone --quiet https://github.com/gsauthof/utility.git
cd utility
git submodule --quiet update --init
EOF

# /usr/bin/zsh would be optimal, but just /bin/zsh is listed in /bin/shells ...
# (unlike in Fedora)
chsh --shell /bin/zsh root
chsh --shell /bin/zsh centos
