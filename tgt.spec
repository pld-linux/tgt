# TODO:
# - init scripts
# - config files
%bcond_with	kernel
#
%include	/usr/lib/rpm/macros.perl
Summary:	Linux SCSI target framework
Name:		tgt
Version:	0.9.4
Release:	0.1
License:	GPL
Group:		Networking/Daemons
Source0:	http://stgt.berlios.de/releases/%{name}-%{version}.tar.bz2
# Source0-md5:	efe76fadd42c4090761be00747c49522
Source1:	%{name}.init
URL:		http://stgt.berlios.de/
BuildRequires:	librdmacm-devel
BuildRequires:	openssl-devel
BuildRequires:	rpm-perlprov >= 4.1-13
BuildRequires:	rpmbuild(macros) >= 1.379
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Linux target framework (tgt) aims to simplify various SCSI target
driver (iSCSI, Fibre Channel, SRP, etc) creation and maintenance. Our
key goals are the clean integration into the scsi-mid layer and
implementing a great portion of tgt in user space.

Target drivers:
- iSCSI software target driver for Ethernet NICs
- iSER software target driver for Infiniband and RDMA NICs
- Virtual SCSI target driver for IBM pSeries
- FCoE software target driver for Ethernet NICs (in progress)
- Qlogic qla2xxx FC target driver (in progress)
- LSI logic FC target driver (not yet)
- Qlogic qla4xxx iSCSI target driver (not yet)
- Virtual SCSI target driver for Xen (obsolete)

Device Emulation :
- SBC: a virtual disk drive that can use a file to store the content.
- SMC: a virtual media jukebox that can be controlled by the "mtx"
  tool (partially functional).
- MMC: a virtual DVD drive that can read DVD-ROM iso files and create
  burnable DVD+R. It can be combined with SMC to provide a fully
  operational DVD jukebox.
- SSC: a virtual tape device (aka VTL) that can use a file to store
  the content (in progress).
- OSD: a virtual object-based storage device that can use a file to
  store the content (in progress).

%prep
%setup -q

sed -i -e 's#-O2#$(OPTFLAGS)#g' usr/Makefile

%build
%{__make} -C usr \
	CC="%{__cc}" \
	OPTFLAGS="%{rpmcppflags} %{rpmcflags}" \
%if %{with kernel}
		KERNELSRC="%{_kernelsrcdir}" \
		IBMVIO=1 \
		FCP=1 \
		FCOE=1 \
%endif
	ISCSI=1 \
	ISCSI_RDMA=1

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/etc/{rc.d/init.d,tgt}
install -d $RPM_BUILD_ROOT{%{_docdir}/%{name},%{_mandir}/man8}

%{__make} -C usr install \
	DESTDIR=$RPM_BUILD_ROOT \
	docdir=$RPM_BUILD_ROOT%{_docdir}/%{name}

install %{SOURCE1}		$RPM_BUILD_ROOT/etc/rc.d/init.d/tgt
install doc/manpages/*.8	$RPM_BUILD_ROOT%{_mandir}/man8
install doc/targets.conf.example	$RPM_BUILD_ROOT/etc/tgt/targets.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add tgt

%preun
if [ "$1" = "0" ]; then
        %service tgt stop
        /sbin/chkconfig --del tgt
fi

%files
%defattr(644,root,root,755)
%doc doc/*.*
%attr(755,root,root) %{_sbindir}/tgt*
%{_mandir}/man8/*
%attr(754,root,root) /etc/rc.d/init.d/tgt
%attr(750, root, root) %dir %{_sysconfdir}/tgt
%attr(750, root, root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/tgt/*.conf
