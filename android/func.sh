
function adids
{
  adb shell 'pm list packages -f' \
      | grep -v '^package:/system/' \
      | sed 's/^.*apk=//' \
      | sort
}

function adview
{
  firefox 'https://play.google.com/store/apps/details?id='"$1"
}

function fdview
{
  firefox 'https://f-droid.org/de/packages/'"$1"/
}

function adinstall
{
  adb shell am start -a android.intent.action.VIEW \
    -d 'market://details?id='"$1" com.android.vending
}

function fdinstall
{
  adb shell am start -a android.intent.action.VIEW \
    -d 'market://details?id='"$1" org.fdroid.fdroid
}
