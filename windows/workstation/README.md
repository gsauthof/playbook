Let's face it, sometimes there is no way around having to use a
Windows system for some time.

The following sections describe some essential software packages
and configuration to make Windows a tiny bit less awful.

Of course, since Windows doesn't have a package manager and
scripting, the configuration tasks can't be easily automated in a
portable way.

## Compose Key

One killer feature of X11 and X11 inspired desktops is the
[Compose key][2]. Entering a special character such as € or ß is then
as easy as `Compose` plus `=` followed by `c` or `Compose` plus
`s` followed by `s`. Thus, one can use the US layout since it's
well suited for programming an VI usage and still be able to
enter all kinds of additional special characters. No need to
switch keyboard layouts then.

The [WinCompose][1] utility brings this behavior to Windows.


## Focus follows mouse

If you are used to [Focus follows mouse][3] not having it easily
drives you insane. Windows even supports it, but each version has
it hidden in different ways. Fortunately, there is a small open
source utility [X-Mouse Controls][4] that enables it on various
versions, e.g. on Windows 10.

## Virtual Machine

If you can't install Linux on a provided work laptop, the next
best thing is to install it in a virtual machine and run it full
screen.

The VM guest might even circumvent some silly USB port controls
an obsessive Windows admin might have configured.

Microsoft provides [Hyper-V][9] but another common choice is to
install [VirtualBox][10], which is even open source (but under
control of Oracle and some extra pieces like USB 3 support under
a proprietary and probably under a unfavorable license).

[VirtualBox][10] compatible images are perhaps more popular than
Hyper-V ones.

In any case, [Vagrant][11] is also available for Windows and it's
a simple way to deploy a guest system to VirtualBox or Hyper-V.

## Cygwin

Sometimes a Windows system is considerably locked down such that
running a virtual machine is out of the question. (This even
extends to the [Windows Subsystem for Windows][12], which
nowadays also is just a virtual machine running Linux. Also, it
isn't installed by default, and can easily be blocked from being
installed.) In that case, the _next_ best thing is to install
[Cygwin][8].

Cygwin provides a UNIX-like environment under Windows, including
a nice terminal, [X-Server][6] and a large [package
repository][7] of the usual open source packages.

A convenient feature of Cygwin is that it [doesn't require
superuser privileges][5] for installation (i.e. call setup with
`setup-x86_64.exe --no-admin`).

See also `cygwin.list` for a selection of essential packages.
After a first install you can automate the package selection a
bit by re-executing the setup like this:

    setup-x86_64.exe --packages $(paste -s -d, cygwin.list)


[1]: https://github.com/SamHocevar/wincompose
[2]: https://en.wikipedia.org/wiki/Compose_key
[3]: https://en.wikipedia.org/wiki/Focus_(computing)#Focus_follows_pointer
[4]: https://github.com/joelpurra/xmouse-controls
[5]: https://www.cygwin.com/faq.html#faq.setup.noroot
[6]: https://x.cygwin.com/docs/ug/setup.html
[7]: https://cygwin.com/packages/
[8]: https://cygwin.com
[9]: https://en.wikipedia.org/wiki/Hyper-V
[10]: https://en.wikipedia.org/wiki/VirtualBox
[11]: https://en.wikipedia.org/wiki/Vagrant_(software)
[12]: https://en.wikipedia.org/wiki/Windows_Subsystem_for_Linux
