
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


