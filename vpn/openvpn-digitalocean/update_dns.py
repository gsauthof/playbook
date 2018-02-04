#!/usr/bin/env python

# 2018, Georg Sauthoff <mail@gms.tf>
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import json
import logging
import os
import subprocess
import sys

log = logging.getLogger(__name__)

class Error(RuntimeError):
  pass

def get_ip_lines():
  xs = subprocess.check_output(['vagrant', 'ssh', '--', 'ip', '-oneline',
    'addr', 'show', 'dev', 'eth0', 'scope', 'global'], universal_newlines=True)
  log.debug('ip addr: {}'.format(xs))
  ls = xs.splitlines()
  if len(ls) < 2 or 'inet' not in xs:
    raise Error('unexpected ssh ip addr output: '.format(xs))
  return ls


def test_extract_addr():
  inp = '''2: eth0    inet 165.227.41.59/20 brd 165.227.47.255 scope global eth0\\       valid_lft forever preferred_lft forever
2: eth0    inet 10.20.0.5/16 brd 10.20.255.255 scope global eth0\\       valid_lft forever preferred_lft forever
2: eth0    inet6 2604:a880:cad:d0::361:5001/64 scope global \\       valid_lft forever preferred_lft forever'''
  assert extract_addr(inp.splitlines()) \
      == [ '165.227.41.59', '10.20.0.5', '2604:a880:cad:d0::361:5001' ]

def extract_addr(ls):
  rs = []
  for i in ls:
    xs = i.split()
    x = xs[3]
    x = x[:x.find('/')]
    rs.append(x)
  return rs

def test_is_private():
  assert is_private('10.20.0.5')
  assert not is_private('165.227.41.59')

def is_private(a):
  return a.startswith('10.') or a.startswith('192.168') or \
      ( a.startswith('172.') and (int(a.split('.')[1]) & 0b1111 == 0b1111 ) )

def is_v4(a):
  return '.' in a

def test_split_addr():
  assert \
      split_addr(['165.227.41.59', '10.20.0.5', '2604:a880:cad:d0::361:5001']) \
        == ( ['165.227.41.59'], ['2604:a880:cad:d0::361:5001'] )

def split_addr(rs):
  v4s = [ x for x in rs if is_v4(x) and not is_private(x) ]
  v6s = [ x for x in rs if not is_v4(x) ]
  return v4s, v6s

def update(hostname, v4s, v6s):
  update_str = 'https://{}/nic/update?myip='.format(hostname)
  if hostname == 'dyn.dns.he.net':
    tail = [ update_str + v4s[0] ]
    if v6s:
      tail.append(update_str + v6s[0])
  else:
    tail = [ update_str + v4s[0] ]
    if v6s:
      tail[0] += '&myipv6=' + v6s[0]
  cmd = [ 'curl', '--fail', '--silent', '--show-error',
      '--proto-redir', '=https',
      '--netrc-file', 'netrc' ] + tail
  log.debug('Calling: ' + ' '.join(cmd))
  o = subprocess.check_output(cmd, universal_newlines=True)
  log.info('{} response: {}'.format(hostname, o))

def main(*a):
  args = parse_args(*a)
  xs = get_ip_lines()
  rs = extract_addr(xs)
  log.debug('Addresses: {}'.format(rs))
  v4s, v6s = split_addr(rs)
  log.debug('Addresses: {} and {}'.format(v4s, v6s))
  c = json.load(open('dns.json'))
  for hostname in c['hostnames']:
    update(hostname, v4s, v6s)

def mk_arg_parser():
  p = argparse.ArgumentParser(
        description='Update dynamic DNS entries')
  p.add_argument('--config', '-c', metavar='CONFIG.JSON',
      help='config file to read the hostnames from (default: dns.json)')
  p.add_argument('--verbose', '-v', action='store_true',
      help='increase verbosity')
  return p

def parse_args(*a):
  arg_parser = mk_arg_parser()
  args = arg_parser.parse_args(*a)
  if args.verbose:
    log.setLevel(logging.DEBUG)
  if not os.path.exists('netrc'):
    raise Error('netrc credentials missing - cf. netrc-sample')
  if not os.path.exists('dns.json'):
    raise Error('dns.json missing  - cf. dns-sample.json')
  return args

log_format      = '%(asctime)s - %(levelname)-8s - %(message)s'
log_date_format = '%Y-%m-%d %H:%M:%S'

if __name__ == '__main__':
  logging.basicConfig(format=log_format, datefmt=log_date_format,
      level=logging.INFO)
  try:
    sys.exit(main())
  except Error as e:
    log.error(e)
    sys.exit(1)
