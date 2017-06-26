A selection of essential [Chromium][chromium]/Chrome extensions.

Main use case: to get a vanilla chromium profile into a useable
state. For example, as part of disaster recovery or when
initializing a fresh `$HOME`.

Generated with [chromium-extensions.py][1].

## Bulk Install

[Chromium][chromium] doesn't allow to fully automate the installation of
extensions, as of 2017-06. The next best thing is a
semi-automatic procedure, like this:

1. make sure that Chromium isn't running
2. execute `chromium-browser $(cut -f1 -d, extension.csv | tail -n +1)`
3. Click on all 'Add to chrome' buttons in all tabs

## Alternatives

A well-known alternative to [AdBlock Plus][abp] is the [uBlock
Origin][ublocko]. In contrast to AdBlock Plus, it was first
released for Chrome and then ported to Firefox. With AdBlock Plus
it was the other way around.

[1]: https://github.com/gsauthof/utility
[abp]: https://chrome.google.com/webstore/detail/adblock-plus/cfhdojbkjhnklbpkdaibdccddilifddb
[chromium]: https://en.wikipedia.org/wiki/Chromium_(web_browser)
[ublocko]: https://chrome.google.com/webstore/detail/ublock-origin/cjpalhdlnbpafiamejdnhcphjbkeiagm
