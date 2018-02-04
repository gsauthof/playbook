#!/bin/bash

set -e

easyrsa=/usr/share/easy-rsa/3/easyrsa
: ${ca_hostname:=ca.example.org}
: ${client_hostname:=client.example.org}

if [ -f etc/openvpn/server.crt ]; then
  echo 'keys already available - doing nothing'
  exit 0
fi
if [ -z "$do_hostname" ]; then
  echo 'do_hostname environment variable not set'
  exit 1
fi
set -x

"$easyrsa" init-pki
# we use the vars file and hostname filenames because
# the build-*-full commands don't support --req-cn and extract
# the CN from the filename (as of easy-rsa 3.0.3)
cp /usr/share/doc/easy-rsa/vars.example pki/vars
echo -e '\n\nset_var EASYRSA_REQ_CN "'"$ca_hostname"'"' >> pki/vars
echo 'set_var EASYRSA_BATCH "yes"' >> pki/vars
"$easyrsa" build-ca nopass
"$easyrsa" build-server-full "$do_hostname" nopass
"$easyrsa" build-client-full "$client_hostname" nopass
openvpn --genkey --secret pki/private/ta.key
mkdir -p etc/openvpn
cp -a pki/private/ta.key etc/openvpn
cp -a pki/private/"$do_hostname".key etc/openvpn/server.key
cp pki/ca.crt etc/openvpn
cp pki/issued/"$do_hostname".crt etc/openvpn/server.crt

ln -s "$client_hostname".crt pki/issued/client.crt
ln -s "$client_hostname".key pki/private/client.key
