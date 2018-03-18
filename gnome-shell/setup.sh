#!/bin/bash

set -x

function gtermset {
    gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:$puuid/ "$1" "$2"
}

function ttermset {
    gsettings set com.gexperts.Tilix.Profile:/com/gexperts/Tilix/profiles/$puuid/ "$1" "$2"
}

gsettings set org.gnome.desktop.input-sources  xkb-options "['compose:ralt']"
gsettings set org.gnome.desktop.interface      clock-show-date true
gsettings set org.gnome.desktop.interface      cursor-blink    false
gsettings set org.gnome.desktop.wm.preferences focus-mode      mouse
gsettings set org.gnome.SessionManager         logout-prompt   false

puuid=$(gsettings get org.gnome.Terminal.ProfilesList default | tr -d "'")
gtermset audible-bell                    false
gtermset background-color                'rgb(0,0,0)'
gtermset background-transparency-percent 10
gtermset default-size-rows               50
gtermset foreground-color                'rgb(0,255,0)'
gtermset scrollbar-policy                never
gtermset use-theme-colors                false
gtermset use-transparent-background      true
gtermset word-char-exceptions            '@ms "-=&#:/.?@+~_%;"'

puuid=$(gsettings get com.gexperts.Tilix.ProfilesList default | tr -d "'")
if [ "$puuid" ]; then
    ttermset background-color                '#000000000000'
    ttermset background-transparency-percent 10
    ttermset foreground-color                '#7373D2D21616'
    ttermset use-theme-colors                false
fi

