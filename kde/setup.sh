#!/bin/bash

set -eux


# 'Search -> File Search'
# 'Enable File Search'
kwriteconfig5 --file baloofilerc --group 'Basic Settings'  --key  Indexing-Enabled       false
# 'Also index file content' (inverted logic)
kwriteconfig5 --file baloofilerc --group  General          --key 'only basic indexing'   true


# 'Power Management -> Energy Saving'
for g in AC Battery LowBattery; do
    # 'When laptop lid closed: Sleep'
    # cf. https://invent.kde.org/plasma/powerdevil/-/blob/master/daemon/powerdevilenums.h
    kwriteconfig5 --file powermanagementprofilesrc --group "$g" --group HandleButtonEvents --key lidAction          1
    # 'When power buton pressed: Sleep'
    # cf. https://invent.kde.org/plasma/powerdevil/-/blob/master/daemon/powerdevilenums.h
    kwriteconfig5 --file powermanagementprofilesrc --group "$g" --group HandleButtonEvents --key powerButtonAction  1
    # 'Even when an external monitor is connected' ('When laptop lid closed')
    kwriteconfig5 --file powermanagementprofilesrc --group "$g" --group HandleButtonEvents --key triggerLidActionWhenExternalMonitorPresent  true

    # 'Suspend session: Automatically Sleep after 10 min' => false
    # XXX unclear if the above disable it as a side effect
done

# 'Workspace -> Shortcuts -> System Settings -> Power Management'
kwriteconfig5 --file kglobalshortcutsrc --group org_kde_powerdevil  --key Sleep 'Meta+End\\tSleep,Sleep,Suspend'

# 'Workspace Behavior -> Screen Locking -> Lock Screen automatically'
kwriteconfig5 --file kscreenlockerrc --group Daemon --key Autolock  false


# 'Window Management -> Window Behavior -> Focus'
# 'Delay focus by'
kwriteconfig5 --file kwinrc --group Windows --key DelayFocusInterval  100
# 'Window activation policy'
kwriteconfig5 --file kwinrc --group Windows --key FocusPolicy         FocusFollowsMouse


# 'Personalization -> Regional Settings -> Region & Language'
kwriteconfig5 --file plasma-localerc --group Formats --key LANG            en_US.UTF-8
kwriteconfig5 --file plasma-localerc --group Formats --key LC_ADDRESS      de_DE.UTF-8
# metric measurements, of course
kwriteconfig5 --file plasma-localerc --group Formats --key LC_MEASUREMENT  C
# swiss-style thousands delimiter
kwriteconfig5 --file plasma-localerc --group Formats --key LC_NUMERIC      en_CH.UTF-8
# ISO/DIN paper formats, of course
kwriteconfig5 --file plasma-localerc --group Formats --key LC_PAPER        C
kwriteconfig5 --file plasma-localerc --group Formats --key LC_TELEPHONE    de_DE.UTF-8
# YYYY-MM-DD dates, of course
kwriteconfig5 --file plasma-localerc --group Formats --key LC_TIME         en_SE.UTF-8


# 'Hardware -> Input Devices -> Keyboard -> Advanced'
# 'Configure keyboard options'
kwriteconfig5 --file kxkbrc --group Layout --key ResetOldOptions   true
# 'Position of Compose key'
kwriteconfig5 --file kxkbrc --group Layout --key Options           compose:ralt


# NB: As f39, Fedora defaults to 'Breeze' 'Application Style' and the 'Fedora' 'Global Theme'
# 'Appearance -> Global Theme -> Colors'
kwriteconfig5 --file kdedefaults/kdeglobals --group General --key ColorScheme   BreezeDark
# 'Appearance -> Global Theme -> Plasma Style' - already the default on Fedora?
kwriteconfig5 --file kdedefaults/plasmarc   --group Theme   --key name          breeze-dark


# 'Hardware -> Input Devices -> Touchpad'
if grep '^N: Name=".*touchpad' -i /proc/bus/input/devices > /dev/null ; then
    gs=$(awk -F '"' '/^N: Name=".*[tT]ouchpad/ { split(prev, a, "[ =]"); printf("--group %d --group %d --group \"%s\"\n", strtonum("0x"a[5]), strtonum("0x"a[7]), $2); exit 0; }  { prev=$0 }' /proc/bus/input/devices)
    # 'Two-finger tap: Middle-click (three-finger tap right-click)'
    kwriteconfig5 --file kcminputrc --group Libinput  $g   LmrTapButtonMap      true
    kwriteconfig5 --file kcminputrc --group Libinput  $g   NaturalScroll        true
    kwriteconfig5 --file kcminputrc --group Libinput  $g   TapToClick           true
    # should be enabled, by default
    # cf.
    # qdbus org.kde.kglobalaccel /org/kde/KWin/InputDevice/$(grep touchpad /sys/class/input/event*/device/name -li | head -n 1 | cut -d/ -f5) org.freedesktop.DBus.Properties.Get org.kde.KWin.InputDevice disableWhileTypingEnabledByDefault
    # DisableWhileTyping=true
fi

# 'Appearance & Style -> Colors & Themes -> Global Theme -> System Sounds'
# 'Enable notifications'
kwriteconfig5 --file kdeglobals   --group Sounds    --key Enable  false


# XXX Color management settings
# hard to automate in a generic fashion



