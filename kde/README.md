This directory contains essential settings to improve the KDE 5 experience.

It's mainly about dark-mode, focus-follows-mouse, compose, better power saving settings and saner defaults, in general.

Those settings may also work on later KDE versions.


## Implementation details

The settings are applied via `kwriteconfig5` which basically just writes entries into ini-style configuration files under `~/.config/`.

This means that when applied from inside a KDE session most settings are effective only after the next login.

NB: `kwriteconfig5` recommends to use `--type bool` with boolean entries, because otherwise it assumes string, but I don't see any advantages when simply using `true`/`false` values.

---

We use `kwriteconfig5` instead of simply distributing selected kde configuration files in a dotfiles repository for several reasons:

1. KDE application tend to not be default minimal, i.e. a kde runtime control file under `~/.config/` often attracts some superfluous settings that are already the default, once it's created for your one or two settings that you actually have changed
2. the KDE config system doesn't allow for drop-ins, i.e. it isn't possible to simply drop some config file snippets into a directory for orthogonal changes
3. the additive nature of a series of `kwriteconfig5` settings allow for easy cherry picking, in case you aren't interested in all of the settings
4. in case affected files already contain independent local changes, those aren't overwritten


## Example

Apply all settings by executing (as the target user):

```
./setup.sh
```


## Hunting Down Filenames and Entries

Some entries can be hunted down by finding the qml file under `/usr/share/kpackage/kcms/` and mapping keys used there to ini entry keys via the right `.kcfg` file.
However, not all kde components use that scheme and not all of those that do package their `.kcfg` under `/usr/share/config.kcfg/`.
Sure, one can also consult `.kcfg` files in the upstream repository.

But perhaps the most convenient approach is to simply snapshot/version `~/.config/` and compare its content after each change applied through KSettings UI to its status quo ante.


## Similar Collections

- https://gitlab.com/TheLinuxNinja/arch-install/-/blob/master/custom-settings-kde.sh
- https://github.com/shalva97/kde-configuration-files/blob/master/scripts/setupKDE.fish
 
