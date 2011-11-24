Name:           akmods
Version:        0.3.8
Release:        3%{?dist}
Summary:        Automatic kmods build and install tool 

Group:          System Environment/Kernel
License:        MIT
URL:            http://rpmfusion.org/Packaging/KernelModules/Akmods
Source0:        akmods
# To be written
#Source1:        akmods.1
Source2:        akmodsbuild
Source3:        akmodsbuild.1
Source4:        akmodsinit
Source6:        akmodsposttrans
Source7:        akmods.service

BuildArch:      noarch

# not picked up automatically
Requires:       %{_bindir}/nohup
Requires:       %{_bindir}/flock
Requires:       %{_bindir}/time

# needed for actually building kmods:
Requires:       %{_bindir}/rpmdev-vercmp
Requires:       kmodtool >= 1-9

# this should track in all stuff that is normally needed to compile modules:
Requires:       bzip2 coreutils diffutils file findutils gawk gcc grep
Requires:       gzip perl make sed tar unzip util-linux which rpm-build

# do we need akmods-{xen,PAE,foo,bar} packages that depend on the proper
# kernel-devel package? Well, maybe later; for now we just go with the 
# easy variant; note that the requires is weak in any case, as a older
# kernel-devel package can provice it as well :-/ 
Requires:       kernel-devel

# we create a special user that used by akmods to build kmod packages
Requires(pre):  shadow-utils

%if %fedora <=16
# for the akmods init script:
Requires(post):  /sbin/chkconfig
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service

%else
# systemd unit requirements.
BuildRequires:  systemd-units
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
%endif


%description
Akmods startup script will rebuild akmod packages during system 
boot while its background daemon will build them for kernels right
after they were installed.

%prep
echo nothing to prep


%build
echo nothing to build


%install
mkdir -p %{buildroot}%{_usrsrc}/akmods/ \
         %{buildroot}%{_localstatedir}/cache/akmods/
install -D -p -m 0755 %{SOURCE0} %{buildroot}%{_sbindir}/akmods
install -D -p -m 0755 %{SOURCE2} %{buildroot}%{_bindir}/akmodsbuild
install -D -p -m 0644 %{SOURCE3} %{buildroot}%{_mandir}/man1/akmodsbuild.1
%if %fedora <=16
install -D -p -m 0755 %{SOURCE4} %{buildroot}%{_initrddir}/akmods
%else
install -D -p -m 0644 %{SOURCE7} %{buildroot}%{_unitdir}/akmods.service
%endif
# %%{_sysconfdir}/kernel/posttrans.d/ should be owned my mkinitrd #441111
install -D -p -m 0755 %{SOURCE6} %{buildroot}/%{_sysconfdir}/kernel/postinst.d/akmods


%pre
# create group and user
getent group akmods >/dev/null || groupadd -r akmods
getent passwd akmods >/dev/null || \
useradd -r -g akmods -d /var/cache/akmods/ -s /sbin/nologin \
    -c "User is used by akmods to build akmod packages" akmods

%post
%if %fedora <=16
# add init script
/sbin/chkconfig --add akmods
# enable init script; users that installed akmods directly or indirectly
# want it to work
if [ $1 = 1 ]; then
   /sbin/chkconfig akmods on
fi
%else
# Systemd
if [ $1 -eq 1 ] ; then 
    # Initial installation
    /bin/systemctl enable akmods.service >/dev/null 2>&1 || :
fi
%endif

%preun
%if %fedora <=16
if [ $1 = 0 ]; then
   /sbin/chkconfig --del akmods
fi
%else
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable akmods.service > /dev/null 2>&1 || :
    /bin/systemctl stop akmods.service > /dev/null 2>&1 || :
fi
%endif


%files 
%{_usrsrc}/akmods
%attr(-,akmods,akmods) %{_localstatedir}/cache/akmods
%{_bindir}/akmodsbuild
%{_sbindir}/akmods
%if %fedora <=16
%{_initrddir}/akmods
%else
%{_unitdir}/akmods.service
%endif
%{_sysconfdir}/kernel/postinst.d/akmods
%{_mandir}/man1/*


%changelog
* Tue Nov 24 2011 Richard Shaw <hobbes1069@gmail.com> - 0.3.8-3
- Kmod can be newer than akmod due to rebuilds for new kernels (#2063)

* Mon Nov 21 2011 Richard Shaw <hobbes1069@gmail.com> - 0.3.8-2
- Add hint about kernel-devel package if rebuild fails due to lack of required
  development files.
- Move logging from /var/cache/akmods/akmods.log to /var/log/akmods.log.

* Fri Sep 23 2011 Richard Shaw <hobbes1069@gmail.com> - 0.3.7-1
- Update to 0.3.7
- Fixes #1805. Version check is now properly based on rpmdev-vercmp exit code.
- Fixes #1813. Exit code is now 0 on success for systemd compatability.
- Fixes #485. Change from "lockfile" to "flock" for lockfile management to
  remove dependency on procmail.
- Fixes #773. Added /usr/bin/time as a requirement.
- Fixes #1592.
- Fixes #1930. "/var/cache/akmods" is now owned by the akmods user. 

* Sun Aug 02 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 0.3.6-3
- add lockfile as hard dep

* Sun Mar 29 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 0.3.6-2
- rebuild for new F11 features

* Sun Feb 01 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info - 0.3.6-1
- update to 0.3.6
-- better posttrans support
-- remove some leftovers from daemon stuff
-- fix a few minor bugs
-- use lockfile

* Thu Jan 29 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info - 0.3.5-1
- update to 0.3.5, fixes #340

* Sun Jan 11 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info - 0.3.4-1
- update to 0.3.4, which has some cosmetic changes

* Thu Oct 02 2008 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info - 0.3.3-2
- rebuild for rpm fusion

* Sun Sep 21 2008 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 0.3.3-1
- proper check for kernel-devel files in akmods as well

* Tue Sep 02 2008 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 0.3.2-1
- Start akmods way earlier (level 05) during boot (#1995)
- proper check for kernel-devel files (#1942)

* Tue Sep 02 2008 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 0.3.1-2
- Remove check section

* Sun May 18 2008 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 0.3.1-1
- Remove check for inotify

* Sat Apr 12 2008 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 0.3.0-1
- Fix thinko in akmodsposttrans

* Sat Apr 12 2008 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 0.3.0-0.4
- split init script and poststrans stuff from akmodsds
- rename akmodsd to akmods
- rename akmodbuild to akmodsbuild
- remove the inotifywatch stuff

* Sun Mar 30 2008 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 0.2.3-1
- update akmodbuid manpage

* Sat Mar 29 2008 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 0.2.2-1
- adjust to recent "arch and flavor in uname" changes from j-rod
- add man page for akmodbuild
- cleanups to akmodbuild

* Thu Jan 31 2008 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 0.2.1-2
- add a hard dep on kmodtool which is needed during akmod building

* Sat Jan 26 2008 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 0.2.1-1
- rename akmods to akmodbuild

* Sun Jan 20 2008 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 0.2.0-1
- require kernel-devel
- use rpmdev-vercmp to compare f a akmods is newer then the installed kmod
- build and install akmods on install

* Wed Jan 09 2007 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 0.1.1-3
- remove akmodstool and integrate it into kmodtool

* Wed Jan 09 2007 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 0.1.1-2
- own /usr/src/akmods

* Sun Jan 06 2007 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 0.1.1-1
- add rpm-build as Require
- add a status function to akmodsd

* Sun Jan 06 2007 Thorsten Leemhuis <fedora[AT]leemhuis[DOT]info> - 0.1.0-1
- Initial RPM release.
