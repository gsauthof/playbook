
## Commands

Extract a list of app ids from your 'my apps' page from your
Google Play account (cf. https://play.google.com/apps):

    $ sed 's@<a@\n<a@g'  myapps_juser.html \
       | grep '^<a href' |  grep https://play.google.com/store/apps/details \
       | awk -F'["=]' '{print $4}' | sort  > juser.ids

Get a list of app ids that are installed on a phone:

    $ adb shell 'pm list packages -f' \
       | awk -F '[:=]' '$2 !~ /\/system\// {print $3}' | sort > nexus.ids

Display the app ids that are not part of the Google Play account:

    $ comm juser.ids nexus.ids -13

Display the app ids that aren't installed, yet:

    $ comm juser.ids nexus.ids -23

Display the already installed app ids:

    $ comm juser.ids nexus.ids -12

Go to the app page in the google store:

    $ function adview { firefox 'https://play.google.com/store/apps/details?id='"$1" }
    $ adview org.videolan.vlc

Start installation of an app from your workstation:

    $ function adinstall { adb shell am start -a android.intent.action.VIEW -d 'market://details?id='"$1" }
    $ adinstall com.termux

Explicitly specify the Google Play Store app:

    $ function adinstall { adb shell am start -a android.intent.action.VIEW -d 'market://details?id='"$1" com.android.vending }
    $ adinstall com.termux

Explicitly specify the F-Droid store app:

    $ function fdinstall { adb shell am start -a android.intent.action.VIEW -d 'market://details?id='"$1" org.fdroid.fdroid }
    $ adinstall com.termux

## Termux

After the [Termux app][termux] is running and the [`openssh` package][ssh] is
installed, installing the default package list is basically just
a matter of setting up ssh. For example:

Inside termux:

    $ mkdir .ssh
    $ cat > .ssh/authorized_keys # copy and paste a pub key
    $ sshd                       # listens on 8022, any username goes

On a workstation:

    $ < termux-package.list ssh android.example.org xargs apt install

Some initial setup (inside termux):

    git clone https://github.com/gsauthof/utility.git
    git clone https://github.com/gsauthof/user-config.git config
    cd config/
    bash install.sh
    cd ..
    pip install ipython

[termux]: https://github.com/termux
[ssh]: https://termux.com/ssh.html

