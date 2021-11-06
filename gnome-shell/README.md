Lists of useful [GNOME Shell][gs] extensions.

- `extension.csv` - a selection of useful GNOME shell extensions
- `attic.csv` - extensions I used in the past

The lists are generated with the [gs-ext.py utility][1].

## Examples

Generate the list:

    $ utility/gs-ext.py > extension.csv

Pretty print:

    $ column -t -s, gnome-shell/extension.csv

Just list the disabled ones:

    $ utility/gs-ext.py -d > attic.csv

Enable an extension:

    $ utility/gs-ext.py --enable some-uuid

Disable an extension:

    $ utility/gs-ext.py --disable some-uuid

Install an extension via the GNOME shell install dialog:

    $ qdbus org.gnome.Shell /org/gnome/Shell org.gnome.Shell.Extensions.InstallRemoteExtension some-uuid

Bulk install (or reinstall/upgrade) all extensions:

    $  cut -f1 -d, extension.csv | xargs utility/gs-ext.py --install
    $  cut -f1 -d, extension.csv | xargs utility/gs-ext.py --enable

Note that `--install` still needs a restart of GNOME Shell (i.e.
logout/login with Wayland).

## More Extensions

See also the official [GNOME Shell extension repository][2].


## Systray - The Neverending Story

On Fedora 26 (GNOME shell 3.24) both top icons extensions for
displaying tray bar icons [easily crash GNOME
shell](https://bugzilla.redhat.com/show_bug.cgi?id=1474022), i.e.
they yield segfaults in the main gnome shell process such that
your session terminates. Thus, as-is, there is no way to have
old-school tray bar icons at the top side-by-side with the GNOME
shell icons. The only reliable option to see the tray icons at
all is to keep the bottom-left tray icon bar expanded after
interactively expanding it (it's minimized, by default).

With Fedora 27 (GNOME shell 3.26) the bottom-left tray icon bar
[isn't available anymore][6]. The TopIcons Plus extension doesn't
crash GNOME shell anymore. But (as of 2018-04) it's unmaintained
and contains a bug where the space of icons of closed programs
isn't freed. It's packaged in the Fedora repository, though.

As of Fedora 33 (GNOME shell 3.38; and also before under Fedora
31), the [TopIcons Plus extension][7] is still available from the main
Fedora package repository and works well enough, i.e. no crashes
and no visual bugs, anymore. The extension is still marked as
unmaintained, although the maintainer accepts pull-requests
and packages releases. Curiously, it even works under Wayland
while the README states the contrary.

When using Fedora 35 (GNOME shell 41), the best choice seems to
be the [AppIndicator][8] extension, since [TopIcons Plus][7]
development stopped and it recommends AppIndicator as a
replacement. Consequently, Fedora 35 doesn't package
TopIcons Plus anymore, but AppIndicator, at least.

It's really unfortunate that Gnome-Shell doesn't support the
traditional system tray area such that one has to install an
extension to use such a basic and proven feature. Even more,
Gnome-Shell developers seem to keep making it harder and harder
for an extension to provide a systray.


## Other Settings

Extensions aren't the only way to customize GNOME Shell.

To make it actually usable you probably want to change the
following settings.

Focus follows mouse:

    gsettings set org.gnome.desktop.wm.preferences focus-mode mouse

Set right-Alt as [Compose key][4]:

    gsettings set org.gnome.desktop.input-sources xkb-options "['compose:ralt']"

Display date in the top bar:

    gsettings set org.gnome.desktop.interface clock-show-date true

Disable blinking cursor:

    gsettings set org.gnome.desktop.interface cursor-blink false

Disable logout confirmation dialog:

    gsettings set org.gnome.SessionManager logout-prompt false

Add logout button (only works on older GNOME Shell versions):

    gsettings set org.gnome.shell always-show-log-out true

For e.g. GNOME Shell 3.24 there is the [Log Out Button][5]
extension.

Better [selection behavior in the terminal][3]:

    puuid=$(gsettings get org.gnome.Terminal.ProfilesList default | tr -d "'")
    gsettings set \
      org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:$puuid/ \
        word-char-exceptions '@ms "-=&#:/.?@+~_%;"'

See also `setup.sh` in this directory for applying the above and
other nice settings in bulk.

[gs]: https://en.wikipedia.org/wiki/GNOME_Shell
[1]: https://github.com/gsauthof/utility
[2]: https://extensions.gnome.org/
[3]: https://unix.stackexchange.com/q/290544/1131
[4]: https://en.wikipedia.org/wiki/Compose_key
[5]: https://gitlab.com/paddatrapper/log-out-button-gnome-extension
[6]: https://blogs.gnome.org/aday/2017/08/31/status-icons-and-gnome/
[7]: https://github.com/phocean/TopIcons-plus
[8]: https://github.com/ubuntu/gnome-shell-extension-appindicator
