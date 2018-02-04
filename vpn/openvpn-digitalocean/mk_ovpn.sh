#!/bin/bash

set -e

if [ $# -lt 1 ]; then
  echo "call: $1 SERVER_HOSTNAME"
  exit 1
fi
if [ $# -gt 1 ]; then
  cd $2
fi

hostname=$1

{
  cat <<EOF
client
dev tun
proto udp
remote $hostname 1194
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
comp-lzo
cipher AES-256-CBC
auth SHA384
# tls-auth key direction - must be the boolean negation
# of the value in server.conf
key-direction 1
EOF
  echo '<ca>'
  cat pki/ca.crt
  echo '</ca>'
  echo '<cert>'
  sed -n '/^--/,/^--/p' pki/issued/client.crt
  echo '</cert>'
  echo '<key>'
  cat pki/private/client.key
  echo '</key>'
  echo '<tls-auth>'
  sed -n '/^--/,/^--/p' pki/private/ta.key
  echo '</tls-auth>'
}
