#!/bin/bash

set -e

if [ -z "$do_token" ]; then
  echo 'exceute: export do_token=my_digital_ocean_API_token'
  exit 1
fi
if [ -z "$do_hostname" ]; then
  echo 'exceute: export do_hostname=my_hostname.example.org'
  exit 1
fi
if [ ! -f netrc ]; then
  echo 'netrc credentials missing - cf. netrc-sample'
  exit 1
fi
if [ ! -f dns.json ]; then
  echo 'dns.json missing  - cf. dns-sample.json'
  exit 1
fi

set -x

vagrant up --provider=digital_ocean
./update_dns.py
vagrant ssh -- shutdown -r now || true

set +x
m=$(echo "1 k $SECONDS 60 / p" | dc)
echo "Provisioned OpenVPN endpoint droplet in $m minutes"
