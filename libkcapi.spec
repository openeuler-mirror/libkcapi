%global sysctl_prio       50
%global sysctl_optmem_max 81920
%global distroname_ext    %{_vendor}

Name:           libkcapi
Version:        1.2.0
Release:        4
Summary:        libkcapi - Linux Kernel Crypto API User Space Interface Library

License:        BSD or GPLv2
URL:            http://www.chronox.de/%{name}.html
Source0:        http://www.chronox.de/%{name}/%{name}-%{version}.tar.xz
Source1:        http://www.chronox.de/%{name}/%{name}-%{version}.tar.xz.asc

Patch0:       libkcapi-1.1.1-lib_Fix_kcapi_handle_destroy_closing_FD_0.patch

BuildRequires:  clang coreutils cppcheck docbook-utils-pdf gcc git hardlink
BuildRequires:  libtool openssl perl systemd xmlto  kernel-headers >= 4.10.0

Requires:       systemd

Provides:       %{name}-tools
Provides:       hmaccalc          == 0.9.14-10.1
Provides:       hmaccalc%{?_isa}  == 0.9.14-10.1
Provides:       %{name}-hmaccalc

Obsoletes:      %{name}-replacements <= %{version}-%{release}
Obsoletes:      %{name}-tools
Obsoletes:      hmaccalc          <= 0.9.14-10
Obsoletes:      %{name}-hmaccalc

%description
The Linux kernel exports a Netlink interface of type AF_ALG to allow user space to utilize the kernel crypto API.
libkcapi uses this Netlink interface and exports easy to use APIs so that a developer does not need to consider the low-level Netlink interface handling.
The library does not implement any cipher algorithms. All consumer requests are sent to the kernel for processing.
Results from the kernel crypto API are returned to the consumer via the library API.

%package        devel
Summary:        Development files for the %{name} package
Requires:       %{name} == %{version}-%{release}

Obsoletes:      %{name}-static
Provides:       %{name}-static

%description    devel
Header files for applications that use %{name}.

%package tests
Summary:        Testing scripts for the %{name} package
Requires:       %{name}%{?_isa}  == %{version}-%{release}
Requires:       %{name}-tools
Requires:       %{name}-hmaccalc
Requires:       coreutils
Requires:       openssl
Requires:       perl

%description    tests
Auxiliary scripts for testing %{name}.

%package_help

%prep
%autosetup -p 1 -S git

cat << EOF > README.%{distroname_ext}
This package increases the default limit of the ancillary buffer size
per kernel socket defined in \`net.core.optmem_max\` to %{sysctl_optmem_max} bytes.

For this preset to become active it requires a reboot after the
installation of this package.  You can also manually increase this
limit by invocing \`sysctl net.core.optmem_max=%{sysctl_optmem_max}\` as the
super-user, e.g. using \`su\` or \`sudo\` on the terminal.

This is done to provide consumers of the new Linux Kernel Crypto API
User Space Interface a well sufficient and reasonable maximum limit
by default, especially when using AIO with a larger amount of IOVECs.

For further information about the AF_ALG kernel socket and AIO, see
the discussion at the kernel-crypto mailing-list:
https://www.mail-archive.com/linux-crypto@vger.kernel.org/msg30417.html

See the instructions given in '%{_sysctldir}/50-default.conf',
if you need or want to override the preset made by this package.
EOF

cat << EOF > %{sysctl_prio}-%{name}-optmem_max.conf
# See the 'README.%{distroname_ext}' file shipped in %%doc
# with the %{name} package.
#
# See '%{_sysctldir}/50-default.conf',
# if you need or want to override this preset.

# Increase the ancillary buffer size per socket.
net.core.optmem_max = %{sysctl_optmem_max}
EOF

%{_bindir}/autoreconf -fiv


%build
%configure               \
  --libdir=/%{_lib}      \
  --disable-silent-rules \
  --enable-kcapi-encapp  \
  --enable-kcapi-dgstapp \
  --enable-kcapi-hasher  \
  --enable-kcapi-rngapp  \
  --enable-kcapi-speed   \
  --enable-kcapi-test    \
  --enable-shared        \
  --enable-static        \
  --enable-sum-prefix=   \
  --enable-sum-dir=/%{_lib} \
  --with-pkgconfigdir=%{_libdir}/pkgconfig
%make_build all doc


%install
%make_install

# Install sysctl.d preset.
mkdir -p %{buildroot}%{_sysctldir}
install -Dpm 0644 -t %{buildroot}%{_sysctldir} %{sysctl_prio}-%{name}-optmem_max.conf

# Install into proper location for inclusion by %%doc.
mkdir -p %{buildroot}%{_pkgdocdir}
install -Dpm 0644 -t %{buildroot}%{_pkgdocdir} README.%{distroname_ext}  README.md CHANGES.md TODO doc/%{name}.p{df,s}
cp -pr lib/doc/html %{buildroot}%{_pkgdocdir}

# Install replacement tools, if enabled.
rm -f %{buildroot}%{_bindir}/md5sum       \
      %{buildroot}%{_bindir}/sha*sum      \
      %{buildroot}%{_bindir}/fips*

find %{buildroot} -type f -name '*.la' -print -delete
find %{buildroot} -type f -name '*.hmac' -print -delete
find %{buildroot} -type f -size 0 -print -delete
find %{buildroot}%{_pkgdocdir} -type f -print | xargs %{__chmod} -c 0644
find %{buildroot}%{_pkgdocdir} -type d -print | xargs %{__chmod} -c 0755

for d in %{_mandir} %{_pkgdocdir}; do
  hardlink -cfv %{buildroot}$d
done

%ldconfig_scriptlets

bin/kcapi-hasher -n sha512hmac %{buildroot}%{_bindir}/sha1hmac   | cut -f 1 -d ' ' > %{buildroot}/%{_lib}/hmaccalc/sha1hmac.hmac
bin/kcapi-hasher -n sha512hmac %{buildroot}%{_bindir}/sha224hmac | cut -f 1 -d ' ' > %{buildroot}/%{_lib}/hmaccalc/sha224hmac.hmac
bin/kcapi-hasher -n sha512hmac %{buildroot}%{_bindir}/sha256hmac | cut -f 1 -d ' ' > %{buildroot}/%{_lib}/hmaccalc/sha256hmac.hmac
bin/kcapi-hasher -n sha512hmac %{buildroot}%{_bindir}/sha384hmac | cut -f 1 -d ' ' > %{buildroot}/%{_lib}/hmaccalc/sha384hmac.hmac
bin/kcapi-hasher -n sha512hmac %{buildroot}%{_bindir}/sha512hmac | cut -f 1 -d ' ' > %{buildroot}/%{_lib}/hmaccalc/sha512hmac.hmac

hardlink -cfv %{buildroot}%{_bindir}
bin/kcapi-hasher -n fipshmac -d %{buildroot}/%{_lib}/fipscheck   %{buildroot}/%{_lib}/libkcapi.so.%{version} || exit 1
ln -s libkcapi.so.%{version}.hmac    %{buildroot}/%{_lib}/fipscheck/libkcapi.so.1.hmac

%check

%files
%doc %dir %{_pkgdocdir}
%doc %{_pkgdocdir}/README.md
%license COPYING*
/%{_lib}/%{name}.so.*
/%{_lib}/fipscheck/%{name}.so.*
%doc %{_pkgdocdir}/README.%{distroname_ext}
%{_sysctldir}/%{sysctl_prio}-%{name}-optmem_max.conf
%{_bindir}/kcapi*
%{_bindir}/sha*hmac
/%{_lib}/hmaccalc/sha*hmac.hmac

%files          devel
%doc %{_pkgdocdir}/CHANGES.md
%doc %{_pkgdocdir}/TODO
%{_includedir}/kcapi.h
/%{_lib}/%{name}.so
%{_libdir}/pkgconfig/%{name}.pc
/%{_lib}/%{name}.a

%files          tests
%{_libexecdir}/%{name}/*

%files          help
%doc %{_pkgdocdir}
%{_mandir}/man1/kcapi*.1.*
%{_mandir}/man3/kcapi_*.3.*

%changelog
* Fri Nov 20 2020 panxiaohe <panxiaohe@huawei.com> - 1.2.0-4
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:Solve the failure when installing libkcapi-devel

* Thu Oct 22 2020 zhangxingliang <zhangxingliang3@huawei.com> - 1.2.0-3
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:Solve the failure when installing libkcapi-tests

* Fri Oct 16 2020 zhangxingliang <zhangxingliang3@huawei.com> - 1.2.0-2
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:Detach the sub package libkcapi-tests from libkcapi

* Fri Jul 17 2020 yang_zhuang_zhuang<yangzhuangzhuang1@huawei.com> - 1.2.0-1
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:update to 1.2.0

* Thu Nov 14 2019 openEuler Buildteam <buildteam@openeuler.org> - 1.1.5-2
- Correct provides of hmaccalc

* Tue Sep 3 2019 openEuler Buildteam <buildteam@openeuler.org> - 1.1.5-1
- Package init
