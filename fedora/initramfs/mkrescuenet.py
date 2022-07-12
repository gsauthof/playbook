#!/usr/bin/python3

# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: © 2020 Georg Sauthoff <mail@gms.tf>

import argparse
import glob
import os
import shutil
import stat
import subprocess
import sys


def mk_arg_parser():
    p = argparse.ArgumentParser(
          formatter_class=argparse.RawDescriptionHelpFormatter,
          description='Install Fedora into a self-contained initramfs image',
          epilog='The resulting image can be used to kexec into.')
    p.add_argument('--no-install', dest='install', action='store_false', default=True,
            help="don't install any packages")
    p.add_argument('--no-network', dest='network', action='store_false', default=True,
            help="don't add default networkd config")
    p.add_argument('--destdir', '-d',
            help=('base directory where to build the initramfs directory tree'
                ' (default: $PWD/initramfs-$family$release'))
    p.add_argument('--release', default='34',
            help='distribution release (default: %(default)s)')
    p.add_argument('--family', default='f',
            help='short distribution family id (default: %(default)s)')
    p.add_argument('--initramfs', '-o',
            help='initramfs archive file (default: $family$release.cpio.$compress)')
    p.add_argument('--vmlinuz',
            help='filename to copy the linux kernel to (default: $family$release.vmlinuz')
    p.add_argument('--gz', dest='compress', const='gz', default='xz', nargs='?',
            help='Use gzip compression (default: xz)')
    p.add_argument('--none', dest='compress', const='', nargs='?',
            help='Use no compression (default: xz)')
    p.add_argument('--print-pkgs', action='store_true',
            help='Print default package list')
    p.add_argument('--packages',
            help='read package list from a file instead of using the default list')
    p.add_argument('--password', '--pw',
            help=('root password read from a file (default: locked account).'
                ' Strips leading/trailing whitespace.'))
    p.add_argument('--salt',
            help='salt used when setting the root password (default: random)')
    p.add_argument('--make', '--mk', action='store_true',
            help='just compress an exsting directory tree')
    p.add_argument('--make-config', '--mk-config', action='store_true',
            help='create secondary cpio archive with new host key, ssh pubkeys')
    p.add_argument('--keys', default='/root/.ssh/authorized_keys',
            help='authorized keys to copy when using --make-config')
    p.add_argument('--level', '-l', default='6',
            help='xz compression level (default: %(default)s)')
    p.add_argument('--no-selinux', dest='selinux', default=True, action='store_true',
            help='persitantly disable selinux')
    return p

def parse_args(*a):
    arg_parser = mk_arg_parser()
    args = arg_parser.parse_args(*a)
    if not args.destdir:
        if args.make_config:
            args.destdir = f'./config-{args.family}{args.release}'
        else:
            args.destdir = f'./initramfs-{args.family}{args.release}'
    args.destdir = os.path.abspath(args.destdir)
    if args.destdir == '/':
        raise RuntimeError('You are using --destdir wrong!')
    if not args.initramfs:
        args.initramfs = args.family + args.release + '.cpio.' + args.compress
        if args.make_config:
            args.initramfs = 'config-' + args.initramfs
    args.initramfs = os.path.abspath(args.initramfs)
    global minimal_pkgs
    if args.packages:
        with open(args.packages) as f:
            minimal_pkgs = [ l[:-1].strip() for l in f if not l.startswith('#') ]
    if args.password:
        with open(args.password) as f:
            args.password = f.read().strip()
    if not args.vmlinuz:
        args.vmlinuz = f'{args.family}{args.release}.vmlinuz'
    args.vmlinuz = os.path.abspath(args.vmlinuz)
    if args.make_config:
        with open(args.keys) as f:
            s = f.read()
            if 'PRIVATE KEY' in s:
                raise RuntimeError('You have to specify public keys with --keys')
    return args

minimal_pkgs = [
    'btrfs-progs',
    'cryptsetup',
    'dosfstools',
    'e2fsprogs',
    'fstransform',
    'git-core',
    'glibc-minimal-langpack',
    'iproute',
    'kernel-modules',
    'less',
    'microdnf',
    'openssh-clients',
    'openssh-server',
    'systemd',
    'systemd-networkd',
    'tmux',
    'vim-minimal',
    'which',
    'xfsprogs',
    'xterm-resize',
]

def install_pkgs(destdir, release):
    subprocess.run(['dnf', '-y',
        '--disablerepo=fedora-modular,updates-modular',
        f'--installroot={destdir}',
        f'--releasever={release}',
        '--setopt=install_weak_deps=false',
        '--setopt=tsflags=nodocs',
        'install'] + minimal_pkgs, check=True)


def compress_licenses(destdir, l=6):
    subprocess.check_output(['hardlink', '-c', 'usr/share/licenses', 'usr/share/doc'],
            text=True, cwd=destdir)
    subprocess.check_output('[ -f licenses.tar.xz ] && tar xf licenses.tar.xz'
            f' || true && tar -c licenses doc | xz -{l} > licenses.tar.xz'
            ' && rm -rf licenses doc',
            shell=True, text=True, cwd=destdir + '/usr/share')

def remove(filename):
    try:
        os.unlink(filename)
    except FileNotFoundError:
        pass

def add_default_nw_config(destdir, network):
    filename = destdir + '/etc/systemd/network/20-wired.network'
    if network:
        with open(filename, 'w') as f:
            print('''[Match]
Name=e*

[Network]
DHCP=ipv4''', file=f)
    else:
        remove(filename)

def disable_ssh_pw_auth(destdir):
    subprocess.check_call(['sed', '-i',
        's/^PasswordAuthentication yes/PasswordAuthentication no/',
        destdir + '/etc/ssh/sshd_config'])
    # e.g. on Fedora 32
    if os.path.exists(destdir + '/etc/ssh/sshd_config.d'):
        with open(destdir + '/etc/ssh/sshd_config.d/99-local.conf', 'w') as f:
            print('PasswordAuthentication no', file=f)


# by default, the selinux-policy package isn't installed
# thus, selinux is disabled in the below is a no-op
def config_selinux(destdir, enable):
    with open(destdir + '/.autorelabel', 'w') as f:
        pass
    fn = destdir + '/etc/selinux/config'
    if not os.path.exists(fn):
        return
    if enable:
        subprocess.check_call(['sed', '-i',
            's/^SELINUX=.*$/SELINUX=permissive/', fn])
    else:
        subprocess.check_call(['sed', '-i',
            's/^SELINUX=.*$/SELINUX=disabled/', fn])

def create_link(target, link_name):
    remove(link_name)
    os.symlink(target, link_name)

def create_links(links):
    for target, link_name in links:
        create_link(target, link_name)

def enable_networkd(destdir):
    try:
        os.mkdir(destdir + '/etc/systemd/system/network-online.target.wants')
    except FileExistsError:
        pass
    # target link_name
    links = [
        ('/usr/lib/systemd/system/systemd-networkd.service',
         'etc/systemd/system/dbus-org.freedesktop.network1.service'),
        ('/usr/lib/systemd/system/systemd-networkd.service',
         'etc/systemd/system/multi-user.target.wants/systemd-networkd.service'),
        ('/usr/lib/systemd/system/systemd-networkd.socket',
         'etc/systemd/system/sockets.target.wants/systemd-networkd.socket'),
        ('/usr/lib/systemd/system/systemd-networkd-wait-online.service',
         'etc/systemd/system/network-online.target.wants/systemd-networkd-wait-online.service'),
    ]
    create_links((target, f'{destdir}/{link_name}')
            for target, link_name in links)

def enable_resolved(destdir):
    # target link_name
    links = [
        ('/usr/lib/systemd/system/systemd-resolved.service',
         'etc/systemd/system/dbus-org.freedesktop.resolve1.service'),
        ('/usr/lib/systemd/system/systemd-resolved.service',
         'etc/systemd/system/multi-user.target.wants/systemd-resolved.service'),
        ('/run/systemd/resolve/resolv.conf',
         'etc/resolv.conf'),
    ]
    create_links((target, f'{destdir}/{link_name}')
            for target, link_name in links)

def disable_repos(destdir):
    repos = [ 'fedora-cisco-openh264.repo', 'fedora-modular.repo',
              'fedora-updates-modular.repo' ]
    repos = [ destdir + '/etc/yum.repos.d/' + x for x in repos ]
    repos = [ x for x in repos if os.path.exists(x) ]
    subprocess.check_call(['sed', '-i', 's/^enabled=1/enabled=0/'] + repos)

def enable_init(destdir):
    create_link('/usr/lib/systemd/systemd', destdir + '/init')

def set_password(destdir, password, salt):
    if password:
        ss = []
        if salt:
            # without the -salt option openssl uses random salt
            ss = [ '-salt', salt ]
        h = subprocess.check_output(['openssl', 'passwd', '-6', '-stdin'] + ss,
                input=password, text=True)
        if h.endswith('\n'):
            h = h[:-1]
    else:
        h = '*'

    shadow = destdir + '/etc/shadow'
    bak    = destdir + '/etc/shadow-'
    shutil.copy2(shadow, bak)
    # we write this as root, thus 0000 permissions aren't an issue here
    with open(bak) as f, open(shadow, 'w') as g:
        for line in f:
            if line.startswith('root:'):
                xs = line.split(':')
                g.write(':'.join([ xs[0], h] + xs[2:]))
            else:
                g.write(line)

# regular expressions are grep-style, i.e. + etc. need to be escaped
ex_paths = [
        'boot/initramfs',
        'etc/udev/hwdb.bin',
        'usr/bin/tzselect',
        'usr/lib/.build-id/',
        'usr/lib/firmware/amdgpu',
        'usr/lib/firmware/mellanox', # switch firmwares
        'usr/lib/firmware/mrvl/prestera', # switch firmwares
        'usr/lib/firmware/qcom', # Qualcom media
        'usr/lib/modules/[^/]\+/vmlinuz',
        'usr/lib64/gconv/IBM', # legacy IBM charsets
        'usr/lib64/gconv/libCNS.so', # charset I don't know
        'usr/lib64/gconv/BIG5HKSCS.so', # charset I don't know
        'usr/share/locale/',
        'usr/share/zoneinfo/',
        'var/cache/',
        'var/lib/dnf/',
        'var/log/dnf',
        'var/log/journal',
        ]

def mk_cpio(destdir, compress, initramfs, ex_paths = None, l = 6):
    if compress == 'gz':
        c = ' | gzip'
    elif compress == 'xz':
        c = f' | xz -{l} --check=crc32'
    else:
        c = ''
    if ex_paths:
        e = (" | grep -z -v '^\./\("
            + '\|'.join(ex_paths)
            + "\)'"
            )
    else:
        e = ''
    cmd = ('find -print0'
            + e
            + ' | cpio --null -o -H newc'
            + c
            + ' > ' + initramfs)
    subprocess.check_call(cmd, shell=True, cwd=destdir)


def cp_kernel(destdir, vmlinuz):
    x = glob.glob(destdir + '/lib/modules/*/vmlinuz')[0]
    shutil.copy(x, vmlinuz)

def make_config(destdir, keys):
    os.makedirs(destdir + '/etc/ssh', exist_ok=True)
    for t in ('ecdsa', 'ed25519', 'rsa'):
        remove(f'{destdir}/etc/ssh/ssh_host_{t}_key')
        remove(f'{destdir}/etc/ssh/ssh_host_{t}_key.pub')
    subprocess.check_call(['ssh-keygen', '-A', '-f', destdir])
    for t in ('ecdsa', 'ed25519', 'rsa'):
        subprocess.check_call(['ssh-keygen', '-l',
            '-f', f'{destdir}/etc/ssh/ssh_host_{t}_key'])
    os.makedirs(destdir + '/root/.ssh', exist_ok=True)
    os.chmod(destdir + '/root', 0o700)
    os.chmod(destdir + '/root/.ssh', 0o700)
    shutil.copy(keys, destdir + '/root/.ssh/authorized_keys')
    os.chmod(destdir + '/root/.ssh/authorized_keys', 0o600)

def mk_unpriv_cpio(destdir, compress, initramfs, l=6):
    if compress == 'gz':
        c = [ 'gzip' ]
    elif compress == 'xz':
        c = [ 'xz', f'-{l}', '--check=crc32' ]
    else:
        c = [ 'cat' ]
    with open(initramfs, 'bw') as f:
        p = subprocess.Popen(['gen_init_cpio', '-'], stdin=subprocess.PIPE,
                stdout=subprocess.PIPE)
        q = subprocess.Popen(c, stdin=p.stdout, stdout=f)
        for path, dns, fns in os.walk(destdir):
            for x in dns:
                filename = os.path.join(path, x)
                relpath = path[len(destdir):] + '/' +  x
                s = os.stat(filename)
                p.stdin.write((f'dir {relpath} {stat.S_IMODE(s.st_mode):04o}'
                        ' 0 0\n').encode())
            for x in fns:
                filename = os.path.join(path, x)
                relpath = path[len(destdir):] + '/' +  x
                s = os.stat(filename)
                p.stdin.write((f'file {relpath} {filename}'
                        f' {stat.S_IMODE(s.st_mode):04o} 0 0\n').encode())
        p.stdin.close()
        q.wait()
        if p.wait():
            raise RuntimeError(f'gen_init_cpio failed: {p.returncode}')


mini_dotfiles = {
        '.vimrc': '''set incsearch
set hlsearch
set ignorecase
set smartcase
set pastetoggle=<F12>
set nomodeline
set ruler
set laststatus=2
set wildmenu
set autoread
set autoindent
set smarttab
set shiftwidth=4
set expandtab
''',
        '.bashrc': '''export LESS=FRi
export SYSTEMD_LESS=FRXMKi
''',
        '.bash_profile': '''. ~/.bashrc
''',
        '.inputrc': '''set editing-mode vi
set blink-matching-paren on
''',
}

def write_mini_dotfiles(destdir):
    for k, v in mini_dotfiles.items():
        with open(f'{destdir}/root/{k}', 'w') as f:
            f.write(v)


def main():
    args = parse_args()
    if args.print_pkgs:
        print('\n'.join(minimal_pkgs))
        return
    if args.make:
        mk_cpio(args.destdir, args.compress, args.initramfs, ex_paths, l=args.level)
        return
    if args.make_config:
        make_config(args.destdir, args.keys)
        if os.getuid():
            mk_unpriv_cpio(args.destdir, args.compress, args.initramfs, l=args.level)
        else:
            mk_cpio(args.destdir, args.compress, args.initramfs, l=args.level)
        return

    if args.install:
        install_pkgs(args.destdir, args.release)
    compress_licenses(args.destdir, l=args.level)
    add_default_nw_config(args.destdir, args.network)
    disable_ssh_pw_auth(args.destdir)
    config_selinux(args.destdir, args.selinux)
    enable_networkd(args.destdir)
    enable_resolved(args.destdir)
    disable_repos(args.destdir)
    enable_init(args.destdir)
    set_password(args.destdir, args.password, args.salt)
    write_mini_dotfiles(args.destdir)

    mk_cpio(args.destdir, args.compress, args.initramfs, ex_paths, l=args.level)
    cp_kernel(args.destdir, args.vmlinuz)

if __name__ == '__main__':
    sys.exit(main())
