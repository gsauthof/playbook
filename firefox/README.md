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
- Better defaults, works against more anti-ad-blocker blockers,
  out of the box

For rewriting Google search result links, the [Search Link
Fix][slf] addon isn't that bad. But it doesn't work with Firefox
on Android. Instead, it explicitly supports the Yandex search
machine. In comparison to this, the [Don't track me
Google][dtmg] addon works fine with Firefox on Android and
additionally supports rewriting the HTTP referrer when following
a search result link (can be disabled in the preferences).

## Theme

Firefox comes with 3 default themes (Dark, Default and Light)
where the Dark one looks decent enough.

## Bookmarked Keyword Searches

The file `bookmarks.html` contains some useful [keyword
searches][ks]. It can be imported from the bookmark editor
(`Ctrl+Shift+O`, 'Import and Backup' and then 'Import Bookmarks
from HTML ...'). A keyword search can be invoked by entering
something like the following in the location bar:

    g firefox
    msgid 12595@star.cs.vu.nl

The Google keyword search (`g`) has two features:

- the search isn't redirected to a language specific Google page
- the results page contains up to 100 results

See also these [blog comments][19] for a discussion of Google
search settings.

## Historic Extensions

With Firefox 57, Mozilla introduced a new API (i.e. the
WebExtensions API) for addons which resulted in some good addons
being pronounced end-of-life. The following contains an overview
of the upgrade paths for a fine addon selection:

- [uBlock Origin][2] - [is ready][3]
- [Self-Destructing Cookies][4] - not compatible and is
  discontinued. A new alternative is
  [Cookie AutoDelete][5] - it even supports Android.
- [User Agent Overrider][6] - not compatible. The [author recommends][8]
  the alternative [User Agent Switcher][7] addon.
- Tree Style Tab - [is ready][9]. Due to webextentsion
  limitations the new version isn't able yet to modify the UI
  much, e.g. it can't remove the horizontal tab bar.
  One can [create a userChrome.css][14] with the necessary
  customizations, though, which I can't recommend enough.
- [Resurrect Pages][10] - [is ready][11]. Due to limitations in
  the new extensions API the resurrect links in the
  page-not-found page are not available, though. Available are
  the links in the context and navigation menus.
- [Vimperator][12] - [is discontinued][13] (the new addon API
  currently misses some functionality) and is even kind of broken
  for the last few Firefox versions before 57. New
  alternatives are [Vim Vixen][vv] and [Tridactyl][tri].
  Unfortunately, currently, I can't give a strong recommendation
  because Vim Vixen included this [security issue][15] and
  Tridactyl doesn't come with good default [key bindings for
  search][16]. Both aren't at the level Vimperator was in its
  best times - in part because the new addon API is too
  restrictive and because these are relatively young projects.
  Both project are actively maintained and are
  continuously improved. AFAICS, Tridactyl is maintained by a
  group of developers while Vim Vixen is a one man show.

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
[14]: https://github.com/gsauthof/user-config/blob/master/.mozilla/firefox/chrome/userChrome.css
[15]: https://github.com/ueokande/vim-vixen/issues/251
[16]: https://github.com/tridactyl/tridactyl/issues/64#issuecomment-496913151
[ff]: https://en.wikipedia.org/wiki/Firefox
[ffa]: https://play.google.com/store/apps/details?id=org.mozilla.firefox
[abp]: https://addons.mozilla.org/en-US/firefox/addon/adblock-plus/
[vv]: https://github.com/ueokande/vim-vixen
[tri]: https://github.com/cmcaine/tridactyl
[slf]: https://github.com/palant/searchlinkfix
[dtmg]: https://github.com/Rob--W/dont-track-me-google
[ks]: http://kb.mozillazine.org/Using_keyword_searches
[19]: https://utcc.utoronto.ca/~cks/space/blog/web/GoogleSearchSettings?showcomments
