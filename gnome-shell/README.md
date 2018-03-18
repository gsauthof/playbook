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

## Dangerous Extensions

On Fedora 26 (GNOME shell 3.24) both top icons extensions for
displaying tray bar icons [easily crash GNOME
shell](https://bugzilla.redhat.com/show_bug.cgi?id=1474022), i.e.
they yield segfaults in the main gnome shell process such that
your session terminates. Thus, as-is, there is no way to have
old-school tray bar icons at the top side-by-side with the GNOME
shell icons. The only reliable option to see the tray icons at
all is to keep the bottom-left tray icon bar expanded after
interactively expanding it (it's minimized, by default).

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
