%global commit 37b0560a2f
%global date 20141114

Name: moose
Summary: Multiscale Neuroscience and Systems Biology Simulator 
Version: 3.0.0
%global codename kheer_kadam
%if %{defined commit}
Release: %{date}.git%{commit}.1%{?dist}
%else
Release: 1%{?dist}
%endif
Url: http://moose.ncbs.res.in/

%if %{defined commit}
#c=%{commit}; GIT_DIR=../moose/.git git archive --prefix=moose_2.0.0_kalakand/ $c | pxz > moose-git$c.tar.xz
Source0: moose-git%{commit}.tar.xz
%else
Source0: http://moose.ncbs.res.in/downloads/%{codename}_%{version}.tgz
%endif
Patch0:  0001-Remove-broken-installation-instructions.patch
Patch1:  0002-Make-moose.desktop-pass-validation.patch

License: LGPLv2

BuildRequires: clang
BuildRequires: rsync
BuildRequires: python2-devel
BuildRequires: gsl-devel
BuildRequires: hdf5-devel
BuildRequires: numpy
BuildRequires: readline-devel
BuildRequires: ncurses-devel
BuildRequires: libsbml-devel
BuildRequires: desktop-file-utils

Requires: numpy
Requires: python-suds
Requires: python-%{name}%{?_isa} = %{version}-%{release}

%description
MOOSE is the base and numerical core for large, detailed simulations
including Computational Neuroscience and Systems Biology. MOOSE spans
the range from single molecules to subcellular networks, from single
cells to neuronal networks, and to still larger systems. It is
backwards-compatible with GENESIS, and forward compatible with Python
and XML-based model definition standards like SBML and NeuroML.

MOOSE uses Python as its primary scripting language. For backward
compatibility we have a GENESIS scripting module, but this is
deprecated. MOOSE uses Qt/OpenGL for its graphical interface. The
entire GUI is written in Python, and the MOOSE numerical code is
written in C++.

%package -n python-%{name}
Summary: Python 2 interface for %{name}
Requires: numpy
Requires: PyQt4
Requires: PyOpenGL
Requires: python-matplotlib
Requires: python-matplotlib-qt4
Requires: python-networkx
%description -n python-%{name}
This package contains the %{summary}.

%package doc
Summary: Documentation and examples for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}

BuildArch: noarch
%description doc
This package contains the documentation and examples for %{name}.

%prep
%setup -q -n %{name}_%{version}_%{codename}
%patch0 -p1
%patch1 -p1
sed -i 's/update-icon-caches/:/; s/chown/:/; s/chmod/:/; s/chgrp/:/; s/strip/:/' Makefile

%global python_cflags %(pkg-config --cflags python)
%global flags BUILD=release PYTHON=2 SVN=0 CXX='clang++ -g' LD='ld --build-id' PYTHON_CFLAGS='%{python_cflags}' USE_READLINE=1 USE_CURSES=1 USE_SBML=1 %{?_smp_mflags}
#         CFLAGS='-Wno-return-type-c-linkage -Wno-nested-anon-types -Wno-unused-variable'

# remove shebangs and fix permissions
rm -v python/libmumbl/*.sh
find python gui Demos -name '*.py' -print0 |xargs -0t sed -i '/\#!\/usr\/bin\/env.*/d'
find python gui Demos -type f \! -name '*.sh' -exec chmod -x {} \;

rm -rf Demos/hopfield  # broken on import
%global binaries gui/mgui.py Demos/izhikevich/Izhikevich.py Demos/squid/squid_demo.py Demos/symcomp/symcomp.py Demos/traub_2005/py/gui.py Demos/traub_2005/py/test_*.py Demos/tutorials/*/*.py Demos/neuroml/CA1PyramidalCell/FvsI_CA1.py Demos/neuroml/GranuleCell/FvsI_Granule98.py Demos/neuroml/LIF/FvsI_LIF.py
sed -i '1 i \#!%{__python2}' %{binaries}
chmod +x %{binaries}

# Upstream uses windows line ending to make things easy for windows users.
# This is unlikely to change until they switch to git.
find Docs -type f \( -name '*.markdown' -o -name '*.txt' \) -print0 |xargs -0t sed -i 's/\r$//'

%build
make %flags libs
make %flags moose
make %flags pymoose

%install
# work around install script trying to mangle $HOME
mkdir -p .home/Desktop
%make_install %flags HOME=$PWD/.home
find %{buildroot} -name '*.py[oc]' -delete
rm %{buildroot}/usr/bin/moosegui
ln -vfs /usr/share/moose/gui/mgui.py %{buildroot}/usr/bin/moosegui

cp moose %{buildroot}%{_bindir}/
rm %{buildroot}%{python_sitelib}/InstallPyMoose.cmake
rm %{buildroot}%{python_sitelib}/setup.py*
find %{buildroot}%{python_sitelib} -name '*.[ch]pp' -delete
find %{buildroot}%{python_sitelib} -type d -empty -delete
rm -r %{buildroot}%{_pkgdocdir}/{markdown,config,user/py,user/build,user/markdown}

%check
desktop-file-validate %{buildroot}/%{_datadir}/applications/%{name}.desktop

%files
%{_bindir}/moose
%{_bindir}/moosegui
%dir %{_datadir}/%{name}/
%{_datadir}/%{name}/gui
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor
%{python_sitelib}/moogli
%{python_sitelib}/libmumbl

%license copyleft

%files doc
%doc %{_pkgdocdir}
%{_datadir}/%{name}/Demos

%files -n python-moose
%{python_sitelib}/%{name}

# taken from https://fedoraproject.org/wiki/Packaging:ScriptletSnippets#Icon_Cache
%post
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%changelog
* Mon Jan 26 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 3.0.0-20141114.git37b0560a2f.1
- Build with sbml

* Tue Nov 25 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 3.0.0-20141114.git37b0560a2f
- New upstream version

* Sat Nov 01 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 2.0.0-20140217.git2addd211a4.1
- Rebuild for libhdf

* Mon Feb 17 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 2.0.0-20140217.git2addd211a4
- Pull from upstream
- Fix debuginfo generation

* Fri Dec 13 2013 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 2.0.0-20131212.gita9a4f5d1dd.3
- add build requirements
- fix installation of /usr/sbin/moose and /usr/bin/moosegui

* Thu Dec 12 2013 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 2.0.0-20131212.gita9a4f5d1dd.2
- fix location of docs on old fedoras

* Thu Dec 12 2013 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 2.0.0-20131212.gita9a4f5d1dd.1
- add more Requires

* Thu Dec 12 2013 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 2.0.0-20131212.gita9a4f5d1dd
- initial package
