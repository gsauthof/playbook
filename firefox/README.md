The `addon.csv` is generated with the [firefox-addons.py utility][1].

## Examples

Generate the list of installed addons:

    $ ./firefox-addons.py -o addons.csv

Open all addon pages in a Firefox window (e.g. for bulk installation):

    $ cut -f1 -d, addon.csv | tail -n +2 | xargs firefox

Pretty print the table:

    $ cut -f1,4- -d, addon.csv| column -t -s,

## Firefox on Android

The CSV file also contains a column that indicates the [Android
on Firefox][ffa] compatibility for each addon. This information
comes from the Mozilla addon web-service, i.e. is what the addon
developer maintains. I can confirm that the positively marked
addons work fine with Firefox on Android. But perhaps is this
information too conservative and some other addons can be forced
to work on Android, as well.

Those addons can be semi-automatically installed via using the
Android Debug Bridge (ADB), e.g. after Firefox is configured as
default browser:

    $ awk -F, '$5 == "true" {print $1}' addon.csv \
        | xargs -r -l adb shell am start -a android.intent.action.VIEW -d

This opens all addons in Firefox Android, one then has to cycle
through the open tabs and touch the install-addon button.

## Firefox 57+

The addons are also marked with respect to their [Firefox 57+
compability][ff57]. Again, this information comes from the
Mozilla addon web-service and might be too conservative. Also,
this is just a snapshot, and the next addon update might add
compatibility.

As of 2017-06-25 the status of some addons is:

- [uBlock Origin][2] - [is ready][3], needs to update the meta-information
- [Self-Destructing Cookies][4] - not compatible. A new alternative is
  [Cookie AutoDelete][5] - although, it doesn't support Firefox on
  Android and LocalStorage, yet.
- [User Agent Overrider][6] - not compatible. The [author recommends][8]
  the alternative [User Agent Switcher][7] addon.
- Tree Style Tab - not compatible. [Work in progress][9].
- [Resurrect Pages][10] - [unclear][11]
- [Vimperator][12] - [a lot of roadblocks][13] (the new addon API
  currently misses some functionality)


## Alternatives

A good alternative to uBlock Origin is [AdBlockPlus][abp]. But
uBlock Origin has the following advantages:

- better defaults - ABP enables some ADs by default - the so
  called 'acceptable ads' - can be easily disabled, though
  (except with Firefox on Android)
- better Firefox on Android support (all configuration options
  are available)
- some additional useful configuration options
- it seems to use less resources (RAM/CPU)




[1]: https://github.com/gsauthof/utility#firefox-addons
[2]: https://addons.mozilla.org/en-US/firefox/addon/ublock-origin/
[3]: https://github.com/gorhill/uBlock/issues/622
[4]: https://addons.mozilla.org/en-US/firefox/addon/self-destructing-cookies/
[5]: https://addons.mozilla.org/en-US/firefox/addon/cookie-autodelete/
[6]: https://addons.mozilla.org/en-US/firefox/addon/user-agent-overrider/
[7]: https://addons.mozilla.org/en-US/firefox/addon/uaswitcher/
[8]: https://github.com/muzuiget/user_agent_overrider
[9]: https://github.com/piroor/treestyletab/issues/1224
[10]: https://addons.mozilla.org/en-US/firefox/addon/resurrect-pages/
[11]: https://github.com/arantius/resurrect-pages/issues/26
[12]: https://addons.mozilla.org/en-US/firefox/addon/vimperator/
[13]: https://github.com/vimperator/vimperator-labs/issues/705
[ff]: https://en.wikipedia.org/wiki/Firefox
[ffa]: https://play.google.com/store/apps/details?id=org.mozilla.firefox
[ff57]: https://blog.mozilla.org/addons/2017/02/16/the-road-to-firefox-57-compatibility-milestones/
[abp]: https://addons.mozilla.org/en-US/firefox/addon/adblock-plus/
