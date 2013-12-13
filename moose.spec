%global commit a9a4f5d1dd
%global date 20131212

Name: moose
Summary: Multiscale Neuroscience and Systems Biology Simulator 
Version: 2.0.0
%global codename kalakand
%if %{defined commit}
Release: %{date}.git%{commit}.2%{?dist}
%else
Release: 1%{?dist}
%endif
Url: http://sourceforge.net/projects/moose

%if %{defined commit}
#c=a9a4f5d1dd; git archive --prefix=moose_2.0.0_kalakand/ $c | xz > moose-git$c.tar.xz
Source0: moose-git%{commit}.tar.xz
%else
#Source0: http://sourceforge.net/projects/moose/files/moose/Moose%202.0.0%20Kalakand/moose_2.0.0_kalakand.src.tar.gz/download
Source0: moose_2.0.0_kalakand.src.tar.gz
%endif

License: LGPLv2

BuildRequires: clang
BuildRequires: rsync
BuildRequires: python2-devel
BuildRequires: gsl-devel
BuildRequires: hdf5-devel
BuildRequires: numpy

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
%description -n python-%{name}
This package contains %{_summary}.

Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: numpy

%prep
%setup -q -n %{name}_%{version}_%{codename}
sed -i 's/if PY3K/ifdef PY3K/' pymoose/moosemodule.cpp
sed -i 's/update-icon-caches/:/; s/chown/:/; s/chmod/:/; s/chgrp/:/;' Makefile

%global flags BUILD=release PYTHON=2 SVN=0 CXX=clang++ %{?_smp_mflags}

%build
make %flags libs
%if %{defined commit}
make %flags moose
%else
make %flags OBJLIBS='$(wildcard */[a-zA-Z]*.o)' moose
%endif
make %flags pymoose

%install
# work around install script trying to mangle $HOME
mkdir /tmp/Desktop
%make_install %flags HOME=/tmp
find %{buildroot} -name '*.py[oc]' -delete
%if %{defined commit}
sed -r -i 's/[?][?][?]/_/' %{buildroot}%{python_sitelib}/moose/neuroml2/generated_neuromlsub.py
%endif
x=$(readlink %{buildroot}/usr/bin/moosegui) && ln -vfs ${x#%{buildroot}} %{buildroot}/usr/bin/moosegui

%files
%{_bindir}/moosegui
%{_datadir}/%{name}/
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/scalable/apps/*

%doc %{_docdir}/%{name}

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
* Thu Dec 12 2013 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 2.0.0-20131212.gita9a4f5d1dd.2
- fix location of docs on old fedoras

* Thu Dec 12 2013 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 2.0.0-20131212.gita9a4f5d1dd.1
- add more Requires

* Thu Dec 12 2013 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 2.0.0-20131212.gita9a4f5d1dd
- initial package
