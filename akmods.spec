Name:           akmods
Version:        0.5.1
Release:        2%{?dist}
Summary:        Automatic kmods build and install tool 

Group:          System Environment/Kernel
License:        MIT
URL:            http://rpmfusion.org/Packaging/KernelModules/Akmods
Source0:        akmods
Source1:        akmods.1
Source2:        akmodsbuild
Source3:        akmodsbuild.1
Source4:        akmods.service.in
Source5:        akmodsposttrans
Source6:        akmods-shutdown
Source7:        akmods-shutdown.service

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

# We use a virtual provide that would match either
# kernel-devel or kernel-PAE-devel
Requires:       kernel-devel-uname-r

# we create a special user that used by akmods to build kmod packages
Requires(pre):  shadow-utils

# systemd unit requirements.
BuildRequires:  systemd-units
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units


%description
Akmods startup script will rebuild akmod packages during system 
boot while its background daemon will build them for kernels right
after they were installed.


%prep
echo Nothing to prep.


%build
echo Nothing to build.


%install
mkdir -p %{buildroot}%{_usrsrc}/akmods/ \
         %{buildroot}%{_localstatedir}/cache/akmods/
install -D -pm 0755 %{SOURCE0} %{buildroot}%{_sbindir}/akmods
install -D -pm 0644 %{SOURCE1} %{buildroot}%{_mandir}/man1/akmods.1
install -D -pm 0755 %{SOURCE2} %{buildroot}%{_bindir}/akmodsbuild
install -D -pm 0644 %{SOURCE3} %{buildroot}%{_mandir}/man1/akmodsbuild.1
install -D -pm 0755 %{SOURCE6} %{buildroot}%{_bindir}/akmods-shutdown
install -D -pm 0755 %{SOURCE5} %{buildroot}%{_sysconfdir}/kernel/postinst.d/akmodsposttrans
install -D -pm 0644 %{SOURCE7} %{buildroot}%{_unitdir}/akmods-shutdown.service

%if 0%{?fedora} >= 18
sed "s|@SERVICE@|display-manager.service|" %{SOURCE4} >\
    %{buildroot}%{_unitdir}/akmods.service
%else
sed "s|@SERVICE@|prefdm.service|" %{SOURCE4} >\
    %{buildroot}%{_unitdir}/akmods.service
%endif


%pre
# create group and user
getent group akmods >/dev/null || groupadd -r akmods
getent passwd akmods >/dev/null || \
useradd -r -g akmods -d /var/cache/akmods/ -s /sbin/nologin \
    -c "User is used by akmods to build akmod packages" akmods

%post
# Systemd
if [ $1 -eq 1 ] ; then 
    # Initial installation
    /bin/systemctl enable akmods.service >/dev/null 2>&1 || :
    /bin/systemctl enable akmods-shutdown.service >/dev/null 2>&1 || :
fi

%preun
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable akmods.service > /dev/null 2>&1 || :
    /bin/systemctl stop akmods.service > /dev/null 2>&1 || :
    /bin/systemctl --no-reload disable akmods-shutdown.service > /dev/null 2>&1 || :
    /bin/systemctl stop akmods-shutdown.service > /dev/null 2>&1 || :
fi


%files 
%{_bindir}/akmodsbuild
%{_bindir}/akmods-shutdown
%{_sbindir}/akmods
%{_sysconfdir}/kernel/postinst.d/akmodsposttrans
%{_unitdir}/akmods.service
%{_unitdir}/akmods-shutdown.service
%{_usrsrc}/akmods
%attr(-,akmods,akmods) %{_localstatedir}/cache/akmods
%{_mandir}/man1/*


%changelog
* Fri Jun 01 2012 Richard Shaw <hobbes1069@gmail.com> - 0.5.1-2
- Add service file to run again on shutdown.
- Add conditional for Fedora 18 to specify correct systemd graphical service.

* Thu Apr 12 2012 Nicolas Chauvet <kwizart@gmail.com> - 0.4.0-4
- Rebuilt

* Tue Mar 20 2012 Richard Shaw <hobbes1069@gmail.com> - 0.4.0-3
- Add additional error output if the needed kernel development files are not
  installed. (Fixes #561)

* Mon Mar 05 2012 Richard Shaw <hobbes1069@gmail.com> - 0.4.0-2
- Remove remaining references to previous Fedora releases
- Remove legacy SysV init script from CVS.
- Added man page for akmods and cleaned up man page for akmodsbuild.

* Tue Feb 07 2012 Nicolas Chauvet <kwizart@gmail.com> - 0.4.0-1
- Update for UsrMove support
- Remove unused references to older fedora
- Change Requires from kernel-devel to kernel-devel-uname-r

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
