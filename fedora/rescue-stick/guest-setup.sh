#!/bin/bash

# Should run inside the guest, e.g. in the virt-builder --run
# virtual environment or at firstboot (virt-builder --firstboot).
#
# Actions should be idempotent.
#
# 2017, Georg Sauthoff <mail@gms.tf>

set -eux

function setup_root
{
  cd /root
  [ -d config ] || \
    git clone https://github.com/gsauthof/user-config.git config
  cd config
  git pull
  git submodule update --init
  ./install.sh
  cd /root
}

function configure_users
{
  useradd -m juser || echo "juser already exists"

  for user in root juser; do
    usermod -s /usr/bin/zsh $user
  done
}

function setup_juser
{
  cd /root
  cp -r .ssh /home/juser
  chown -R juser:juser /home/juser

  for filename in /home/juser/first-boot-user.sh ; do
    cat <<EOF > "$filename"
set -eux

cd /home/juser
[ -d config ] || \
  git clone https://github.com/gsauthof/user-config.git config
cd config
git pull
git submodule update --init
./install.sh
cd /home/juser
[ -d utility ] || \
  git clone https://github.com/gsauthof/utility.git
cd utility
git pull
EOF
    chown juser:juser "$filename"
    su - juser "$filename"
  done
}

function adjust_etc
{
  cd /root
  git config --global user.email "root@example.com"
  git config --global user.name "Root User"
  git --work-tree=/etc --git-dir=etc.git init

  cat <<EOF > /etc/sysctl.d/01-disk-bufferbloat.conf
vm.dirty_background_bytes=107374182
vm.dirty_bytes=214748364
EOF

  cd ~/etc.git
  git add sysctl.d/01-disk-bufferbloat.conf
  git commit -m 'add anti-bufferbloat sysctl config' || true
}

function configure_fstab
{
  git add fstab
  git commit -m 'add fstab' || true

  sed -i 's/^\(UUID=.\+ swap\)/#\1/' /etc/fstab
  git add fstab
  git commit -m 'disable swap' || true

  sed -i 's/^\(UUID=.\+\/.\+defaults\>\)/\1,noatime/' /etc/fstab
  git add fstab
  git commit -m 'disable atime writing' || true
}

function configure_grub
{
  git add default/grub
  git commit -m 'add default/grub' || true

  sed -i 's/^\(GRUB_CMDLINE_LINUX=.\+\)"$/\1 bochs_drm.fbdev=off quiet"/' /etc/default/grub
  git add default/grub
  git commit -m 'silence, disable framebuffer when running inside qemu

seriously, what is the point? besides breaking -display curses ...' \
      || true

  find /boot -name grub.cfg -exec grub2-mkconfig -o  '{}' ';'
}

function reuse_swap
{
  local disk=/dev/$(lsblk -r | grep 'part /boot' | cut -d' ' -f1 | tr -d '[0-9]')

  if [ $(sfdisk --dump "$disk" | grep "^$disk"2 -c) = 0 ]; then
    return
  fi

  umount "$disk"1
  sfdisk --delete "$disk" 2
  echo ',+,' | sfdisk -N 1 "$disk" --no-reread
  partprobe
  # resize2fs requires a not too long ago fsck run
  e2fsck -f -p "$disk"1
  resize2fs "$disk"1
}

# apparently when running inside virt-builder/virt-customize --run
# environment $HOME=/ ...
if [ "$HOME" != "/root" ]; then
  export HOME=/root
fi

setup_root
configure_users
setup_juser
adjust_etc
configure_fstab
configure_grub
reuse_swap


