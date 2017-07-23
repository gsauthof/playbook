#!/bin/bash

set -x

gsettings set org.gnome.desktop.input-sources xkb-options "['compose:ralt']"
gsettings set org.gnome.desktop.interface clock-show-date true
gsettings set org.gnome.desktop.interface cursor-blink false
gsettings set org.gnome.desktop.wm.preferences focus-mode mouse
gsettings set org.gnome.SessionManager logout-prompt false

pid=$(dconf read /org/gnome/terminal/legacy/profiles:/default | tr -d "'")
dconf write /org/gnome/terminal/legacy/profiles:/:$pid/word-char-exceptions '@ms "-=&#:/.?@+~_%;"'
