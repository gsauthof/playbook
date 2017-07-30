#!/usr/bin/env python3

# 2017, Georg Sauthoff <mail@gms.tf>


import argparse
import configparser
import datetime
import functools
import glob
import hashlib
import json
import logging
import operator
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid


log = logging.getLogger(__name__)
cnf = {}

log_format      = '{rel_secs:6.1f} {lvl}  {message}'
log_date_format = '%Y-%m-%d %H:%M:%S'

class Relative_Formatter(logging.Formatter):
  level_dict = { 10 : 'DBG',  20 : 'INF', 30 : 'WRN', 40 : 'ERR',
      50 : 'CRI' }
  def format(self, rec):
    rec.rel_secs = rec.relativeCreated/1000.0
    rec.lvl = self.level_dict[rec.levelno]
    return super(Relative_Formatter, self).format(rec)

def setup_logging():
  logging.basicConfig(format=log_format, datefmt=log_date_format,
      level=logging.DEBUG)
  logging.getLogger().handlers[0].setFormatter(
      Relative_Formatter(log_format, log_date_format, style='{'))

def setup_file_logging(filename):
  log = logging.getLogger()
  fh = logging.FileHandler(filename)
  fh.setLevel(logging.DEBUG)
  f = Relative_Formatter(log_format, log_date_format, style='{')
  fh.setFormatter(f)
  log.addHandler(fh)

def mk_arg_parser():
  p = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Setup a Fedora system',
        epilog='...')
  p.add_argument('--config', '-c', metavar='FILENAME', default='system.cnf',
      help='.ini style config file (default: system.cnf)')
  p.add_argument('--state', metavar='FILENAME', default='cnf.state',
      help='cache progress')
  p.add_argument('--clean', action='store_true', help='remove state')
  p.add_argument('--stage', required=True, type=int, help='Configuration stage - stage 0 creates the base system from scratch, stage 1 assumes to run in the target system')
  p.add_argument('--log', nargs='?', const='config.log', metavar='FILENAME',
      help='capture log message to file (default: config.log)')
  p.add_argument('--mount', action='store_true',
      help='just mount everything')
  p.add_argument('--umount', action='store_true',
      help='just umount everything')
  return p

def parse_args(*a):
  arg_parser = mk_arg_parser()
  args = arg_parser.parse_args(*a)
  return args

def read_config(filename):
  c = configparser.ConfigParser()
  c.read_dict({
        'target': {
          'etc-mirror': '/root/etc-mirror',
          'init-user': 'false',
          'locale': 'LANG=en_US.UTF-8',
          'restore-postfix': 'false',
          'restore-postgres': 'false',
          'setup-pamu2f': 'false',
          'timezone': 'Europe/Berlin'
        },
        'init': {
          'cryptsetup': 'true'
        }
      })
  c.read(filename)
  if 'release' not in c['target']:
    c['target']['release'] = check_output(['rpm', '-E' '%fedora'])\
        .stdout.strip()
  return c


def file_hash(filename):
  h = hashlib.sha256()
  with open(filename, 'rb', buffering=0) as f:
    for b in iter(lambda : f.read(128*1024), b''):
      h.update(b)
  return h.hexdigest()


def check_file_hash(filename, hash):
  h = file_hash(filename)
  if h != hash:
    raise RuntimeError('sha256({})={} != {}'.format(filename, h, hash))

done_set = set()
state = { 'stage0': {}, 'stage1': {} }

def load_state(args):
  filename = args.state
  global done_set
  global state
  if not os.path.exists(filename):
    return
  with open(filename, 'r') as f:
    d = json.load(f)
    key = 'stage{}'.format(args.stage)
    if key in d:
      state[key] = d[key]
      if 'done_set' in state[key]:
        done_set = set(state[key]['done_set'])

def store_state(args):
  filename = args.state
  global state
  log.debug('Storing state as {}'.format(filename))
  with open(filename, 'w') as f:
    state['stage{}'.format(args.stage)]['done_set'] = list(done_set.__iter__()) 
    json.dump(state, f)

def mark_done(slug):
  global done_set
  done_set.add(slug)
  store_state(args)

def skip_this(slug):
  global done_set
  return slug in done_set

class SkipThis(Exception):
  pass

def execute_once(fn):
  @functools.wraps(fn)
  def guard(*xs, **ys):
    if skip_this(fn.__name__):
      log.info('Skipping {}'.format(fn.__name__))
    else:
      log.info('Running {}'.format(fn.__name__))
      try:
        r = fn(*xs, **ys)
        mark_done(fn.__name__)
        return r
      except SkipThis:
        log.info('Skipping {} because of configuration'.format(fn.__name__))
        return
  return guard

def quote_arg(x):
  def need_quotes(x):
    meta_char = [ '|', '&', ';', '(', ')', '<', '>', ' ', '\t' ]
    other = [ "'", '"', '`', '$' ]
    for c in meta_char + other:
      if c in x:
        return True
    return False
  if need_quotes(x):
    r = x.replace("'", """'"'"'""")
    return "'" + r + "'"
  return x

def test_quote_arg():
  assert quote_arg('mdadm') == 'mdadm'
  assert quote_arg('foo bar') == "'foo bar'"
  assert quote_arg('<foo>') == "'<foo>'"
  assert quote_arg("'foo'bar") == """''"'"'foo'"'"'bar'"""

def run_output(cmd2, redact_input=False, chroot=False, sudo=None, *xs, **ys):
  prefix = []
  if chroot:
    prefix = [ 'chroot', '/mnt/new-root' ]
  if sudo:
    prefix += [ 'sudo', '-u', sudo, '--set-home' ]
  cmd = prefix + cmd2
  call = ' '.join(quote_arg(x) for x in cmd)
  if 'input' in ys:
    if redact_input:
      i = '<secret>'
    else:
      i = ys['input'].replace('\n', '\\n')
    log.debug("Calling: echo -ne '{}' | {}".format(i, call))
  else:
    log.debug('Calling: ' + call)
  r = subprocess.run(cmd, *xs, stdout=subprocess.PIPE,
      stderr=subprocess.PIPE, universal_newlines=True, **ys)
  return r

def test_run_output_simple():
  r = run_output(['true'])
  assert r.returncode == 0

def test_run_output():
  r = run_output(['echo', 'hello'])
  assert r.stdout == 'hello\n'
  assert r.stderr == ''

def check_output(cmd, *xs, **ys):
  r = run_output(cmd, *xs, **ys)
  if r.returncode != 0:
    call = ' '.join("'{}'".format(x) for x in cmd)
    raise RuntimeError(
        'Command exited with: {}\nCall: {}\n    Stdout: {}\n    Stderr: {}'
        .format(r.returncode, call, r.stdout, r.stderr)
        + ('    Stdin: {}'.format(ys['input']) if 'input' in ys else '') )
  return r

def test_check_output():
  import pytest
  with pytest.raises(RuntimeError) as e:
    check_output(['false'])
  assert e.value.args[0] == '''Command exited with: 1
Call: 'false'
    Stdout: 
    Stderr: '''

def test_check_output2():
  import pytest
  with pytest.raises(RuntimeError) as e:
    check_output(['awk', 'END {print "23";print "42">"/dev/stderr";exit(2)}', '/dev/null'])
  assert e.value.args[0] == '''Command exited with: 2
Call: 'awk' 'END {print "23";print "42">"/dev/stderr";exit(2)}' '/dev/null'
    Stdout: 23

    Stderr: 42
'''

def test_check_output_ok():
  r = check_output(['awk', 'END {print "23";print "42">"/dev/stderr"}', '/dev/null'])
  assert r.returncode == 0
  assert r.stdout == '23\n'
  assert r.stderr == '42\n'

def download(url, filename):
  check_output(['curl', '-f', '-L', '-o', filename, url])

def dnf_install(pkgs, **ys):
  pkgs = pkgs if isinstance(pkgs, list) else [ pkgs ]
  check_output(['dnf', '-y', 'install'] + pkgs, **ys)

def dnf_installroot(pkgs, group=False):
  pkgs = pkgs if isinstance(pkgs, list) else [ pkgs ]
  if group:
    cmd = [ 'group', 'install' ]
  else:
    cmd = [ 'install' ]
  release = cnf['init']['release']
  check_output(['dnf', '-y', '--installroot=/mnt/new-root',
    '--releasever={}'.format(release)] + cmd + pkgs)

def commit_etc(filenames, msg):
  mirror = cnf['target']['etc-mirror']
  git_dir = '--git-dir=' + mirror
  filenames = filenames if isinstance(filenames, list) else [ filenames ]
  check_output(['git', git_dir, 'add'] + filenames)
  run_output(['git', git_dir, 'commit', '-m', msg])

def line_edit(filename, fn):
  with tempfile.NamedTemporaryFile(mode='w', delete=False,
      dir=os.path.dirname(filename)) as tmp, open(filename) as f:
    for line in f:
      if line.endswith('\n'):
        line = line[:-1]
      x = fn(line)
      print(x, file=tmp)
  os.chmod(tmp.name, os.stat(filename).st_mode & 0o7777)
  os.rename(tmp.name, filename)

def test_line_edit():
  with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
    print('hello', file=f)
    print('23', file=f)
  def fn(line):
    if line.startswith('hello'):
      return line + ' world'
    return line
  line_edit(f.name, fn)
  with open(f.name) as g:
    assert g.read() == '''hello world
23
'''
  os.unlink(f.name)

def test_line_edit_perm():
  with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
    print('hello', file=f)
  os.chmod(f.name, 0o700)
  def fn(line):
    pass
  line_edit(f.name, fn)
  assert os.stat(f.name).st_mode & 0o7777 == 0o700
  os.unlink(f.name)


@execute_once
def mk_etc_mirror():
  mirror = cnf['target']['etc-mirror']
  etc = '/etc'
  git_dir = '--git-dir=' + mirror
  os.makedirs(mirror, exist_ok=True)
  if os.path.exists(mirror + '/HEAD'):
    log.warn('Reusing already initialized git repo: {}'.format(mirror))
  else:
    check_output(['git', '--work-tree='+etc, git_dir, 'init'])
  check_output(['git', git_dir, 'config', 'user.email',
      cnf['target']['git-mail']])
  check_output(['git', git_dir, 'config', 'user.name',
      cnf['target']['git-name']])

@execute_once
def commit_core_files():
  commit_etc(['crypttab', 'fstab', 'default/grub'], 'add core etc files')

# cf. https://unix.stackexchange.com/a/40857/1131
@execute_once
def add_rpmfusion():
  d = cnf['self']['download-dir']
  release = cnf['target']['release']
  rpm_name = d  + '/rpmfusion-free-release-{}.noarch.rpm'.format(release)
  key_name = d + '/RPM-GPG-KEY-rpmfusion-free-fedora-{}'.format(release)
  if not os.path.exists(key_name):
    download('https://rpmfusion.org/keys?action=AttachFile&do=get&target='
        + 'RPM-GPG-KEY-rpmfusion-free-fedora-{}'.format(release), key_name)
  r = check_output(['gpg2', '--with-fingerprint', key_name])
  if r.stdout.splitlines()[1]\
      .endswith('E4EE E113 33C9 3091 8D8E  638D 20C7 C9D6 9690 E4AF'):
      raise RuntimeError('gpg fingerprint mismatch for {}'.format(key_name))
  check_output(['rpm', '--import', key_name])
  if not os.path.exists(rpm_name):
    download('https://download1.rpmfusion.org/free/fedora/'
        + 'rpmfusion-free-release-{}.noarch.rpm'.format(release), rpm_name)
  check_output(['rpm', '--checksig', rpm_name])
  dnf_install(rpm_name)
  commit_etc(glob.glob('/etc/pki/rpm-gpg/RPM-GPG-KEY-rpmfusion*')
           + glob.glob('/etc/yum.repos.d/rpmfusion*'), 'add rpmfusion repo' )

@execute_once
def add_livna():
  d = cnf['self']['download-dir']
  rpm_name = d  + '/livna-release.rpm'
  rpm_hash = '18d08b96bc0d6912ba2e957a33ff5c50d7f8f3bae710f5186f3ebc0c78458e13'
  if not os.path.exists(rpm_name):
    download('http://rpm.livna.org/livna-release.rpm', rpm_name)
  check_file_hash(rpm_name, rpm_hash)
  dnf_install(rpm_name)
  commit_etc(['pki/rpm-gpg/RPM-GPG-KEY-livna', 'yum.repos.d/livna.repo'],
      'add livna repo')

@execute_once
def set_host():
  hostname = cnf['target']['hostname']
  ls = [ 'hosts' ]
  if os.path.exists('/etc/hostname'):
    ls.append('hostname')
  commit_etc(ls, 'add hosts')
  check_output(['hostnamectl', 'set-hostname', hostname])
  def f(line):
    if line.startswith('127.0.0.1') or line.startswith('::1'):
      if (' ' + hostname) not in line:
        return line + ' ' + hostname
    return line
  line_edit('/etc/hosts', f)
  commit_etc(['hostname', 'hosts'], 'set hostname')


# we ony care about stable IPv6 addresses, i.e.:
# IPV6_ADDR_GEN_MODE=eui64
# (we would get the other keys by default, too)
default_eth_nm_conf = '''HWADDR={}
TYPE=Ethernet
BOOTPROTO=dhcp
DEFROUTE=yes
PEERDNS=yes
PEERROUTES=yes
IPV4_FAILURE_FATAL=no
IPV6INIT=yes
IPV6_AUTOCONF=yes
IPV6_DEFROUTE=yes
IPV6_PEERDNS=yes
IPV6_PEERROUTES=yes
IPV6_FAILURE_FATAL=no
IPV6_ADDR_GEN_MODE=eui64
NAME={}
UUID={}
ONBOOT=yes
AUTOCONNECT_PRIORITY=-999
'''

eth_re = re.compile('^[0-9]+: ([^:]+):.+link/ether ([^ ]+) .+$')

def default_eth():
  r = check_output(['ip', '-o', 'link'])
  for line in r.stdout.splitlines():
    if 'link/ether' in line:
      m = eth_re.match(line)
      if m:
        log.info('Autodected default ethernet device {} (mac: {})'
            .format(m.group(1), m.group(2)))
        return m.groups()
  return ( cnf['target']['eth'], cnf['target']['mac'])

# cf. https://unix.stackexchange.com/q/331129/1131
@execute_once
def set_ipv6():
  eth, mac = default_eth()
  filename = '/etc/sysconfig/network-scripts/ifcfg-{}'.format(eth)
  if os.path.exists(filename):
    commit_etc([filename], 'add default eth config')
  with open(filename, 'w') as f:
    f.write(default_eth_nm_conf.format(mac, eth, uuid.uuid4()))
  commit_etc([filename], 'use eui-64 derived ipv6 address')

@execute_once
def set_ssh():
  filename = '/etc/ssh/sshd_config'
  commit_etc([filename], 'add ssh/sshd_config')
  def f(line):
    if line.startswith('PasswordAuthentication yes'):
      return 'PasswordAuthentication no'
    return line
  line_edit(filename, f)
  commit_etc([filename], 'disable sshd password auth')
  # with Fedora 26 minimal custom-environment/minimal-environment
  # sshd is installed/enabled by default - just to be sure ...
  check_output(['systemctl', 'start', 'sshd.service'])
  check_output(['systemctl', 'enable', 'sshd.service'])
  check_output(['systemctl', 'reload', 'sshd.service'])

# https://lwn.net/Articles/682582/
# https://lwn.net/Articles/708476/
@execute_once
def disable_bufferbloat():
  filename = '/etc/sysctl.d/01-disk-bufferbloat.conf'
  if os.path.exists(filename):
    commit_etc(filename, 'add 01-disk-bufferbloat.conf')
  with open(filename, 'w') as f:
    print('''vm.dirty_background_bytes=107374182
vm.dirty_bytes=214748364''', file=f)
  commit_etc(filename, 'add anti-bufferbloat sysctl config')
  check_output(['sysctl', '--load', filename])

@execute_once
def set_shell():
  zsh = '/usr/bin/zsh'
  if not os.path.exists(zsh):
    raise RuntimeError('There is no {}'.format(zsh))
  commit_etc(['passwd', 'shadow', 'group', 'gshadow' ], 'add passwd ...')
  users = [ 'root', cnf['target']['user'] ]
  for user in users:
    check_output(['usermod', '--shell', zsh, user])
  commit_etc(['passwd', 'shadow', 'group', 'gshadow' ], 'change user shell to zsh')

@execute_once
def set_dotfiles():
  # other user homes are just restored from backup, by default
  homes = [ ('/root', 'root' ) ]
  if cnf['target']['init-user'] == 'true':
    homes.append( ('/home/'+cnf['target']['user'], cnf['target']['user']) )
  for home, user in homes:
    sudo = user if user != 'root' else None
    work_dir = home + '/config'
    if os.path.exists(work_dir):
      check_output(['git', 'pull'], cwd=work_dir, sudo=sudo)
    else:
      check_output(['git', 'clone',
          'https://github.com/gsauthof/user-config.git', work_dir ],
          sudo=sudo)
      check_output(['git', 'submodule', 'update', '--init' ], cwd=work_dir)
    check_output(['./install.sh'], cwd=work_dir, sudo=sudo)

@execute_once
def clone_utility():
  homes = [ ('/root', 'root' ) ]
  if cnf['target']['init-user'] == 'true':
    homes.append( ('/home/'+cnf['target']['user'], cnf['target']['user']) )
  for home, user in homes:
    sudo = user if user != 'root' else None
    work_dir = home + '/utility/'
    if os.path.exists(work_dir):
      check_output(['git', 'pull'], cwd=work_dir, sudo=sudo)
    else:
      check_output(['git', 'clone',
          'https://github.com/gsauthof/utility.git', work_dir], sudo=sudo)

@execute_once
def install_packages():
  with open('package.list') as f:
    pkgs = f.read().splitlines()
    log.info('Installing {} packages ...'.format(pkgs.__len__()))
    dnf_install(pkgs)
  commit_etc(['passwd', 'shadow', 'group', 'gshadow' ],
      'record users/groups created by newly installed packages')

# unwanted packages that are part of an installed package group
# Example: the harmful 'tracker' package, which is included in
# the @workstation-product-environment
# cf. https://bugzilla.redhat.com/show_bug.cgi?id=747689
#     https://bugzilla.redhat.com/show_bug.cgi?id=1271872
@execute_once
def remove_packages():
  filename = 'unpackage.list'
  if not os.path.exists(filename):
    raise SkipThis()
  with open(filename) as f:
    pkgs = f.read().splitlines()
    log.info('Installing {} packages ...'.format(pkgs.__len__()))
    run_output(['dnf', '-y', 'remove'] + pkgs)


@execute_once
def disable_avahi():
  check_output(['systemctl', 'disable',
      'avahi-daemon.socket', 'avahi-daemon.service'])
  check_output(['systemctl', 'stop',
      'avahi-daemon.socket', 'avahi-daemon.service'])
  #systemctl mask avahi-daemon.socket avahi-daemon.service

def personalize_main_cf():
  host = cnf['target']['hostname']
  m = re.match('^([^.]+)(\.|$)', host)
  short = m.group(1)
  def f(line):
    if line.startswith('mydomain '):
      return 'mydomain = {}'.format(host)
    elif line.startswith('myhostname '):
      return 'myhostname = {}'.format(host)
    elif line.startswith('mydestination '):
      return 'mydestination = {0}.localdomain localhost.localdomain localhost {0} {1}'\
          .format(short, host)
    else:
      return line
  line_edit('/etc/postfix/main.cf', f)

@execute_once
def restore_postfix():
  if cnf['target']['restore-postfix'] != 'true':
    raise SkipThis()
  old_etc = cnf['self']['old-etc']
  commit_etc(['postfix/main.cf', 'postfix/master.cf', 'postfix/virtual',
    'postfix/transport', 'aliases'], 'add vanilla postfix config')
  pf_files = [ 'sender_relay', 'sasl_passwd', 'sender_transport', 'main.cf' ]
  files = [ 'postfix/' + x for x in pf_files ] + [ 'aliases' ]
  check_output(['rsync', '-aiR']
      + [ '{}/./{}'.format(old_etc, x) for x in files ] + [ '/etc' ])
  personalize_main_cf()
  check_output(['chmod', '640', '/etc/postfix/sasl_passwd'])
  commit_etc(files, 'configure postfix')
  check_output(['postalias', '/etc/aliases'])
  for i in [ 'sender_relay', 'sasl_passwd', 'sender_transport' ]:
    check_output(['postmap', '/etc/postfix/{}'.format(i)])
  check_output(['systemctl', 'restart', 'postfix.service'])
  check_output(['systemctl', 'enable', 'postfix.service'])

@execute_once
def restore_postgres():
  if cnf['target']['restore-postgres'] != 'true':
    raise SkipThis()
  old_var = cnf['self']['old-var']
  check_output(['rsync', '-a', old_var + '/lib/pgsql/data', '/var/lib/pgsql'])
  check_output(['postgresql-setup', '--upgrade'])

@execute_once
def restore_etc():
  if 'custom-etc-files' not in cnf['target']:
    raise SkipThis()
  old_etc = cnf['self']['old-etc']
  files = cnf['target']['custom-etc-files'].split()
  es = [ x for x in files if os.path.exists('/etc/'+x) ]
  commit_etc(es, 'add vanilla etc files')
  check_output(['rsync', '-aiR']
      + [ '{}/./{}'.format(old_etc, x) for x in files ] + [ '/etc' ])
  commit_etc(files, 'restore misc etc files')

@execute_once
def enable_services():
  if 'enable-services' not in cnf['target']:
    raise SkipThis()
  services = cnf['target']['enable-services'].split()
  for service in services:
    check_output(['systemctl', 'enable', service])

@execute_once
def set_locale():
  locale = cnf['target']['locale']
  def f():
    names = [ 'locale.conf', 'vconsole.conf']
    return [ i for i in names if os.path.exists('/etc/'+i) ] 
  commit_etc(f(), 'add locale conf')
  check_output(['localectl', 'set-locale', locale])
  commit_etc(f(), 'update locale')

@execute_once
def set_timezone():
  tz = cnf['target']['timezone']
  check_output(['ln', '-sf', '../usr/share/zoneinfo/Europe/Berlin', '/etc/localtime'])

@execute_once
def set_pam_u2f():
  if cnf['target']['setup-pamu2f'] != 'true':
    raise SkipThis()
  old_etc = cnf['self']['old-etc']
  u2f_map = [ i for i in [ 'u2f_map', 'u2f_mappings' ]
      if os.path.exists(old_etc + '/' + i) ][0]
  shutil.copy(old_etc + '/' + u2f_map, '/etc/u2f_map')
  snippet = '''
# assuming pamu2fcfg defaults,
# equivalent to adding: origin=pam://$hostname appid=pam://$hostname
# add `debug` option for verbose troubleshooting
auth requisite pam_u2f.so authfile=/etc/u2f_map interactive
'''
  filenames = ['pam.d/login', 'pam.d/gdm-password']
  commit_etc(filenames + ['u2f_map'], 'add pam files')
  def f(state, line):
    if state[0]:
      return line
    if 'pam_u2f.so' in line:
      state[0] = True
    if line.startswith('auth') and 'substack' in line \
        and ('system-auth' in line or 'password-auth' in line ):
      return '\n' + snippet + '\n' + line
    else:
      return line
  for filename in filenames:
    line_edit('/etc/' + filename, functools.partial(f, [False]))
  commit_etc(filenames, 'enable u2f auth')
  # work around SELinux policy bug, cf.
  # https://bugzilla.redhat.com/show_bug.cgi?id=1377451
  check_output(['semanage', 'permissive', '-a', 'local_login_t'])

def set_tlp():
  tlp = '/etc/default/tlp'
  if not os.path.exists(tlp):
    raise SkipThis()
  snippet = '''# disabled due to this warning:
# https://wiki.archlinux.org/index.php/TLP
#SATA_LINKPWR_ON_BAT=min_power
SATA_LINKPWR_ON_BAT=max_performance'''
  def f(line):
    if line.startswith('SATA_LINKPWR_ON_BAT=min_power'):
      return snippet
    else:
      return line
  commit_etc(tlp, 'add default/tlp')
  line_edit(tlp, f)
  commit_etc(tlp, 'be conservative about SATA link-power settings ...')

def stage1():
  mk_etc_mirror()
  commit_core_files()
  add_rpmfusion()
  add_livna()
  set_host()
  set_ipv6()
  set_locale()
  set_timezone()
  set_ssh()
  disable_bufferbloat()
  set_shell()
  set_dotfiles()
  clone_utility()
  install_packages()
  remove_packages()
  disable_avahi()
  set_tlp()
  restore_postfix()
  restore_postgres()
  restore_etc()
  enable_services()
  set_pam_u2f()
  return 0

def has_partitions(dev):
  r = check_output(['sfdisk', '--list', dev])
  for line in r.stdout.splitlines():
    if line.startswith(dev):
      return True
  return False

def get_devices():
  devs = [ cnf['init']['device'] ]
  if 'mirror' in cnf['init']:
    devs.append(cnf['init']['mirror'])
  return devs

@execute_once
def create_partitions():
  devs = get_devices()
  for dev in devs:
    if has_partitions(dev):
      check_output(['sfdisk', '--delete', dev])
    check_output(['sfdisk', dev],
        input='size=1GiB, type=83, bootable\ntype=83\n')

def get_password():
  with open(cnf['init']['password-file']) as f:
    pw = f.read().splitlines()[0].strip()
    return pw

@execute_once
def mk_fs():
  global state
  devs = get_devices()
  if devs.__len__() == 1:
    boot_dev = devs[0] +'1'
  else:
    boot_dev = '/dev/md/new-boot'
    u = str(uuid.uuid4())
    check_output(['mdadm', '--create', boot_dev, '--run', '--level=1',
        '--uuid', u,
        '--raid-devices=2' ] + [ x+'1' for x in devs ] )
    state['stage0']['boot-raid1-uuid'] = u
  u = str(uuid.uuid4())
  check_output(['mkfs.ext4', '-U', u, boot_dev ])
  state['stage0']['fs-uuid'] = { 'boot' : u }
  root_dev = []
  if cnf['init']['cryptsetup'] == 'true':
    pw = get_password()
    state['stage0']['luks-uuid'] = []
    for i, dev in enumerate(devs):
      u = str(uuid.uuid4())
      check_output(['cryptsetup', 'luksFormat', dev + '2',
        '--key-file', '-', '--uuid', u], input=pw, redact_input=True)
      state['stage0']['luks-uuid'].append(u)
      d = 'new-root-{}'.format(i)
      check_output(['cryptsetup', 'luksOpen', dev + '2', d,
        '--key-file', '-'], input=pw, redact_input=True)
      root_dev.append('/dev/mapper/'+d)
  else:
    root_dev = [ dev + '2' for dev in devs ]
  u = str(uuid.uuid4())
  flags = [ '--data', 'raid1' ] if 'mirror' in cnf['init'] else []
  check_output(['mkfs.btrfs', '--uuid', u ] + flags + root_dev)
  state['stage0']['fs-uuid']['root'] = u
  os.makedirs('/mnt/new-root', exist_ok=True)
  check_output(['mount', '-o', 'noatime', root_dev[0], '/mnt/new-root'])
  for sub_vol in [ 'root', 'home' ]:
    check_output(['btrfs', 'subvolume', 'create',
      '/mnt/new-root/' + sub_vol ])
  check_output(['umount', '/mnt/new-root'])
  if cnf['init']['cryptsetup'] == 'true':
    for i, dev in enumerate(devs):
      check_output(['cryptsetup', 'luksClose', 'new-root-{}'.format(i)])

def mount_fs():
  if 'mirror' in cnf['init']:
    run_output(['mdadm', '--assemble', '--scan'])
  if cnf['init']['cryptsetup'] == 'true':
    pw = get_password()
    for i, uuid in enumerate(state['stage0']['luks-uuid']):
      check_output(['cryptsetup', 'luksOpen',
        '/dev/disk/by-uuid/'+uuid, 'new-root-{}'.format(i),
        '--key-file', '-'], input=pw, redact_input=True)
  os.makedirs('/mnt/new-root', exist_ok=True)
  check_output(['mount', '-o', 'noatime,subvol=root',
    'UUID='+state['stage0']['fs-uuid']['root'], '/mnt/new-root'])
  os.makedirs('/mnt/new-root/home', exist_ok=True)
  check_output(['mount', '-o', 'noatime,subvol=home',
    'UUID='+state['stage0']['fs-uuid']['root'], '/mnt/new-root/home'])
  os.makedirs('/mnt/new-root/boot', exist_ok=True)
  check_output(['mount', '-o', 'noatime',
    'UUID='+state['stage0']['fs-uuid']['boot'], '/mnt/new-root/boot'])

def umount_fs():
  for point in [ 'new-root/boot', 'new-root/home', 'new-root' ]:
    check_output(['umount', '/mnt/' + point ])
  if cnf['init']['cryptsetup'] == 'true':
    for i, uuid in enumerate(state['stage0']['luks-uuid']):
      check_output(['cryptsetup', 'luksClose', 'new-root-{}'.format(i)])

def bind_mount():
  for point in [ 'dev', 'proc', 'sys' ]:
    d = '/mnt/new-root/'+point
    os.makedirs(d, exist_ok=True)
    check_output(['mount', '--bind', '/'+point, d])

def is_mounted(point):
  with open('/proc/self/mounts') as f:
    s = f.read()
    return ' {} '.format(point) in s

def bind_umount():
  se_mount = '/mnt/new-root/sys/fs/selinux'
  if is_mounted(se_mount):
    check_output(['umount', se_mount])
  for point in [ 'dev', 'proc', 'sys' ]:
    check_output(['umount', '/mnt/new-root/'+point])

@execute_once
def install_base():
  dnf_installroot('system-release')
  # the custom-environment and minimal-environment groups seem to be identical
  dnf_installroot('custom-environment', group=True)
  dnf_installroot(['grub2', 'cryptsetup', 'btrfs-progs', 'mdadm',
      'git', 'zsh'])

@execute_once
def mk_crypttab():
  if cnf['init']['cryptsetup'] != 'true':
    raise SkipThis()
  luks_conf = 'luks-{0} UUID={0} none'
  crypttab = '/mnt/new-root/etc/crypttab'
  with open(crypttab, 'w') as f:
    for uuid in state['stage0']['luks-uuid']:
      print(luks_conf.format(uuid), file=f)

@execute_once
def mk_fstab():
  fstab_conf = '''UUID={0:}    /boot    ext4     defaults,noatime    1 2
UUID={1:}    /        btrfs    subvol=root,x-systemd.device-timeout=0,noatime    0 0
UUID={1:}    /home    btrfs    subvol=home,x-systemd.device-timeout=0,noatime    0 0'''
  fstab = '/mnt/new-root/etc/fstab'
  with open(fstab, 'w') as f:
    print(fstab_conf.format(state['stage0']['fs-uuid']['boot'],
        state['stage0']['fs-uuid']['root']), file=f)

# Even without real serial hardware available - configuring it just in case
# makes sense as fallback when running inside qemu.
# The bochs_drm is disabled for a better user experience inside a
# text-mode qemu (cf. https://unix.stackexchange.com/a/347751/1131).
@execute_once
def mk_grub_defaults():
  grub_conf = '''GRUB_TIMEOUT=5
GRUB_DISTRIBUTOR=Fedora
GRUB_DEFAULT=saved
GRUB_DISABLE_SUBMENU=true
GRUB_TERMINAL_OUTPUT=console
GRUB_CMDLINE_LINUX="{}quiet console=tty0 console=ttyS0,115200 bochs_drm.fbdev=off"
GRUB_DISABLE_RECOVERY=true'''
  grub_default = '/mnt/new-root/etc/default/grub'
  with open(grub_default, 'w') as f:
    luks = ''
    if cnf['init']['cryptsetup'] == 'true':
      luks = ''.join('rd.luks.uuid={} '.format(x)
                     for x in state['stage0']['luks-uuid'])
    print(grub_conf.format(luks), file=f)

def refresh_chroot():
  shutil.copy('/etc/resolv.conf', '/mnt/new-root/etc/')

@execute_once
def install_inside_chroot():
  dnf_install('kernel', chroot=True)

@execute_once
def install_grub():
  # with efi-boot, it is another location ...
  check_output(['grub2-mkconfig', '-o', '/boot/grub2/grub.cfg'], chroot=True)

  devs = get_devices()
  for dev in devs:
    check_output(['grub2-install', dev], chroot=True)

def has_user(user):
  with open('/mnt/new-root/etc/passwd') as f:
    for line in f:
      if line.startswith(user + ':'):
        return True
  return False

@execute_once
def create_user():
  user = cnf['target']['user']
  if has_user(user):
    log.info('Not creating user {} because it is already present'.format(user))
  else:
    check_output(['useradd', '--groups', 'wheel', '--create-home', user],
        chroot=True)

@execute_once
def set_user_password():
  pw = get_password()
  users = [ 'root', cnf['target']['user'] ]
  inp = ''.join([ '{}:{}\n'.format(user, pw) for user in users ])
  check_output(['chpasswd'], input=inp, chroot=True, redact_input=True)

def count_relabel(s):
  i = 0
  for line in s.splitlines():
    if line.startswith('Relabeled'):
      i += 1
  return i

def print_sshd_fingerprints():
  s = 'sshd host key fingeprints:'
  for name in glob.glob('/mnt/new-root/etc/ssh/ssh_host*key'):
    r = check_output(['ssh-keygen', '-l', '-f', name])
    s += '\n    ' + r.stdout.strip()
  log.info(s)

def fix_selinux_context():
  check_output(['load_policy', '-i'], chroot=True)
  es = [ '/proc', '/dev', '/sys' ]
  excluded = functools.reduce(operator.add, [ [ '-e', e] for e in es ], [])
  r = check_output(['restorecon', '-rv', ] + excluded + [ '/' ], chroot=True)
  log.info('Relabeled {} files'.format(count_relabel(r.stdout)))
  os.makedirs('/mnt/new-root/mnt/tmp', exist_ok=True)
  # cf. https://bugzilla.redhat.com/show_bug.cgi?id=1412696#c32
  check_output(['mount', '--bind', '/mnt/new-root', '/mnt/new-root/mnt/tmp'])
  for e in es:
    check_output(['chcon', '--reference='+e, '/mnt/tmp'+e], chroot=True)
  check_output(['umount', '/mnt/new-root/mnt/tmp'])

@execute_once
def set_authorized_keys():
  if 'authorized-keys' not in cnf['init']:
    raise SkipThis()
  os.makedirs('/mnt/new-root/root/.ssh', mode=0o700, exist_ok=True)
  ak = '/mnt/new-root/root/.ssh/authorized_keys'
  with open(ak, 'w') as f:
    print(cnf['init']['authorized-keys'], file=f)
  os.chmod(ak, 0o600)

@execute_once
def mk_host_keys():
  check_output(['ssh-keygen', '-A'], chroot=True)


def stage0():
  run_output(['setenforce', '0'])
  create_partitions()
  mk_fs()
  mount_fs()
  bind_mount()
  install_base()
  mk_crypttab()
  mk_fstab()
  mk_grub_defaults()
  refresh_chroot()
  install_inside_chroot()
  install_grub()
  create_user()
  set_authorized_keys()
  set_user_password()
  mk_host_keys()
  print_sshd_fingerprints()
  fix_selinux_context()
  bind_umount()
  umount_fs()
  return 0

def run(args):
  if args.stage == 1:
    stage1()
  elif args.stage == 0:
    if args.mount:
      mount_fs()
      bind_mount()
    elif args.umount:
      bind_umount()
      umount_fs()
    else:
      stage0()
  else:
    raise RuntimeError('Unknown stage: {}'.format(args.stage))
  return 0

def imain(*a):
  global args
  args = parse_args(*a)
  if args.log:
    setup_file_logging(args.log)
  log.info(('Started at {:' + log_date_format + '}')
      .format(datetime.datetime.now()))
  if args.clean and os.path.exists(args.state):
    os.remove(args.state)
  load_state(args)
  global cnf
  cnf = read_config(args.config)
  r = run(args)
  store_state(args)
  return r

def main(*a):
  setup_logging()
  return imain(*a)

if __name__ == '__main__':
  sys.exit(main())



