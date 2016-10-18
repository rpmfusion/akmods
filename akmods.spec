Name:           akmods
Version:        0.5.6
Release:        1%{?dist}
Summary:        Automatic kmods build and install tool 

License:        MIT
URL:            http://rpmfusion.org/Packaging/KernelModules/Akmods

Source0:        https://github.com/hobbes1069/%{name}/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

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
%setup -q


%build
echo Nothing to build.


%install
mkdir -p %{buildroot}%{_usrsrc}/akmods \
         %{buildroot}%{_sbindir} \
         %{buildroot}%{_sysconfdir}/kernel/postinst.d \
         %{buildroot}%{_unitdir} \
         %{buildroot}%{_localstatedir}/cache/akmods \
         %{buildroot}%{_prefix}/lib/systemd/system-preset
install -pm 0755 akmods %{buildroot}%{_sbindir}/
install -pm 0755 akmodsbuild %{buildroot}%{_sbindir}/
install -pm 0755 akmods-shutdown %{buildroot}%{_sbindir}/
install -pm 0755 akmodsposttrans %{buildroot}%{_sysconfdir}/kernel/postinst.d/
install -pm 0644 akmods-shutdown.service %{buildroot}%{_unitdir}/

sed "s|@SERVICE@|display-manager.service|" akmods.service.in >\
    %{buildroot}%{_unitdir}/akmods.service

install -pm 0644 95-akmods.preset %{buildroot}%{_prefix}/lib/systemd/system-preset/

# Generate and install man pages.
mkdir -p %{buildroot}%{_mandir}/man1
help2man -N -i akmods.h2m -s 1 \
    -o %{buildroot}%{_mandir}/man1/akmods.1 akmods
help2man -N -i akmods.h2m -s 1 \
    -o %{buildroot}%{_mandir}/man1/akmodsbuild.1 akmodsbuild


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
* Fri Oct 14 2016 Richard Shaw <hobbes1069@gmail.com> - 0.5.6-1
- Disable shutdown systemd service file by default.
- Remove modprobe line from main service file.

* Wed Aug 17 2016 Sérgio Basto <sergio@serjux.com> - 0.5.4-3
- New release

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
