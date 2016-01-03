Name:           akmods
Version:        0.5.4
Release:        2%{?dist}
Summary:        Automatic kmods build and install tool 

License:        MIT
URL:            http://rpmfusion.org/Packaging/KernelModules/Akmods

Source0:        akmods
Source1:        akmodsbuild
Source2:        akmodsposttrans
Source3:        akmods.service.in
Source4:        akmods-shutdown
Source5:        akmods-shutdown.service
Source6:        akmods.h2m
Source7:        95-akmods.preset

BuildArch:      noarch

BuildRequires:  help2man

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
BuildRequires:  systemd
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd


%description
Akmods startup script will rebuild akmod packages during system 
boot while its background daemon will build them for kernels right
after they were installed.


%prep
echo Nothing to prep.


%build
echo Nothing to build.


%install
mkdir -p %{buildroot}%{_usrsrc}/akmods \
         %{buildroot}%{_localstatedir}/cache/akmods \
         %{buildroot}%{_prefix}/lib/systemd/system-preset
install -D -pm 0755 %{SOURCE0} %{buildroot}%{_sbindir}/akmods
install -D -pm 0755 %{SOURCE1} %{buildroot}%{_sbindir}/akmodsbuild
install -D -pm 0755 %{SOURCE4} %{buildroot}%{_sbindir}/akmods-shutdown
install -D -pm 0755 %{SOURCE2} %{buildroot}%{_sysconfdir}/kernel/postinst.d/akmodsposttrans
install -D -pm 0644 %{SOURCE5} %{buildroot}%{_unitdir}/akmods-shutdown.service

sed "s|@SERVICE@|display-manager.service|" %{SOURCE3} >\
    %{buildroot}%{_unitdir}/akmods.service

install -pm 0644 %{SOURCE7} %{buildroot}%{_prefix}/lib/systemd/system-preset/

# Generate and install man pages.
mkdir -p %{buildroot}%{_mandir}/man1
help2man -N -i %{SOURCE6} -s 1 \
    -o %{buildroot}%{_mandir}/man1/akmods.1 %{SOURCE0}
help2man -N -i %{SOURCE6} -s 1 \
    -o %{buildroot}%{_mandir}/man1/akmodsbuild.1 %{SOURCE1}


%pre
# create group and user
getent group akmods >/dev/null || groupadd -r akmods
getent passwd akmods >/dev/null || \
useradd -r -g akmods -d /var/cache/akmods/ -s /sbin/nologin \
    -c "User is used by akmods to build akmod packages" akmods

%post
%systemd_post akmods.service
%systemd_post akmods-shutdown.service

%preun
%systemd_preun akmods.service
%systemd_preun akmods-shutdown.service

%postun
%systemd_postun akmods.service
%systemd_postun akmods-shutdown.service


%files 
%{_sbindir}/akmodsbuild
%{_sbindir}/akmods-shutdown
%{_sbindir}/akmods
%{_sysconfdir}/kernel/postinst.d/akmodsposttrans
%{_unitdir}/akmods.service
%{_unitdir}/akmods-shutdown.service
%{_prefix}/lib/systemd/system-preset/95-akmods.preset
%{_usrsrc}/akmods
%attr(-,akmods,akmods) %{_localstatedir}/cache/akmods
%{_mandir}/man1/*


%changelog
* Sun Jan 03 2016 Nicolas Chauvet <kwizart@gmail.com> - 0.5.4-2
- Revert conflicts kernel-debug-devel

* Thu Jul 23 2015 Richard Shaw <hobbes1069@gmail.com> - 0.5.4-1
- Do not mark a build as failed when only installing the RPM fails.
- Run akmods-shutdown script instead of akmods on shutdown.
- Add systemd preset file to enable services by default.

* Wed Jul 15 2015 Richard Shaw <hobbes1069@gmail.com> - 0.5.3-2
- Add package conflicts to stop pulling in kernel-debug-devel, fixes BZ#3386.
- Add description for the formatting of the <kernel> parameter, BZ#3580.
- Update static man pages and clean them up.
- Fixed another instance of TMPDIR causing issues.
- Added detection of dnf vs yum to akmods, fixed BZ#3481.

* Wed Apr  1 2015 Richard Shaw <hobbes1069@gmail.com> - 0.5.2-1
- Fix temporary directory creation when TMPDIR environment variable is set,
  fixes BZ#2596.
- Update systemd scripts to use macros.
- Fix akmods run on shutdown systemd unit file, fixes BZ#3503.

* Sun Nov 16 2014 Nicolas Chauvet <kwizart@gmail.com> - 0.5.1-4
- Fix akmods on armhfp - rfbz#3117
- Use yum instead of rpm to install packages - rfbz#3350
  Switch to a better date format

* Fri Jan 11 2013 Richard Shaw <hobbes1069@gmail.com> - 0.5.1-3
- Really fix akmods.service.in.

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
