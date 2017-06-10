
function adids
{
  adb shell 'pm list packages -f' \
      | awk -F '[:=]' '$2 !~ /\/system\// {print $3}' | sort
}

function adview
{
  firefox 'https://play.google.com/store/apps/details?id='"$1"
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
