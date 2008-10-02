Name:           akmods
Version:        0.3.3
Release:        2%{?dist}
Summary:        Automatic kmods build and install tool 

Group:          System Environment/Kernel
License:        MIT
URL:            http://rpmfusion.org/Packaging/KernelModules/Akmods
Source0:        akmods
#to be written: Source1:        akmods.1
Source2:        akmodsbuild
Source3:        akmodsbuild.1
Source4:        akmodsinit
Source6:        akmodsposttrans
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch

# needed for actually building kmods:
#Requires:       %{_bindir}/inotifywait
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

# for the akmods init script:
Requires(post):  /sbin/chkconfig
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service


%description
Akmods startup script will rebuild akmod packages during system 
boot while its background daemon will build them for kernels right
after they were installed.

%prep
echo nothing to prep


%build
echo nothing to build


%install
rm -rf $RPM_BUILD_ROOT
mkdir -p \
   $RPM_BUILD_ROOT/%{_usrsrc}/akmods/ \
   $RPM_BUILD_ROOT/%{_localstatedir}/cache/akmods/
install -D -p -m 0755 %{SOURCE0} $RPM_BUILD_ROOT/%{_sbindir}/akmods
install -D -p -m 0755 %{SOURCE2} $RPM_BUILD_ROOT/%{_bindir}/akmodsbuild
install -D -p -m 0644 %{SOURCE3} ${RPM_BUILD_ROOT}%{_mandir}/man1/akmodsbuild.1
install -D -p -m 0755 %{SOURCE4} $RPM_BUILD_ROOT/%{_initrddir}/akmods
# %%{_sysconfdir}/kernel/posttrans.d/ should be owned my mkinitrd #441111
install -D -p -m 0755 %{SOURCE6} $RPM_BUILD_ROOT/%{_sysconfdir}/kernel/postinst.d/akmods

%clean
rm -rf $RPM_BUILD_ROOT

%pre
# create group and user
getent group akmods >/dev/null || groupadd -r akmods
getent passwd akmods >/dev/null || \
useradd -r -g akmods -d /var/cache/akmods/ -s /sbin/nologin \
    -c "User is used by akmods to build akmod packages" akmods

%post
# add init script
/sbin/chkconfig --add akmods
# enable init script; users that installed akmods directly or indirectly
# want it to work
if [ $1 = 1 ]; then
   /sbin/chkconfig akmods on
fi

%preun
if [ $1 = 0 ]; then
   /sbin/chkconfig --del akmods
fi


%files 
%defattr(-,root,root,-)
%{_usrsrc}/akmods
%{_localstatedir}/cache/akmods/
%{_bindir}/akmodsbuild
%{_sbindir}/akmods
%{_initrddir}/akmods
%{_sysconfdir}/kernel/postinst.d/akmods
%{_mandir}/man1/*

%changelog
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
