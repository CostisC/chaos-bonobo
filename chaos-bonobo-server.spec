#
# spec file for package chaos-bonobo-server
#
#

Name:           chaos-bonobo-server
Version:        %{_version}
Release:        %{_release}
Summary:        The Chaos-Bonobo Server
License:        Apache
Packager:       CostisC
BuildArch:      noarch
Requires:       nodejs

%global dest /usr/share/%{name}
%global etc /etc/chaos-bonobo

%description
The Server counterpart of the Chaos Bonobo framework.
Quick instructions:
* rpm -ivh %{name}-%{version}-%{release}.%{_arch}.rpm
* systemctl start %{name}
* Read the documentation in http://localhost:4440/docs



%install
mkdir -p %{buildroot}%{dest} %{buildroot}%{etc}
mkdir -p %{buildroot}/etc/systemd/system/
mkdir -p %{buildroot}/var/log/%{name}
cp -a docs/ node_modules/ bonobo-server.js logger.json %{buildroot}%{dest}
install server.conf experiment.yaml %{buildroot}%{etc}
cp chaos-bonobo-server.service /%{buildroot}/etc/systemd/system/


%post
systemctl daemon-reload
#systemctl try-restart %{name}

%preun
if [ $1 -eq 0 ]; then
   systemctl disable --no-reload %{name}
   systemctl stop %{name}
fi

%postun
if [ $1 -eq 0 ]; then
   systemctl daemon-reload
   systemctl reset-failed
   rm -rf %{dest} /var/log/%{name}
fi


%clean

%files
%defattr(0644, root, root)
%dir %{etc}
%config(noreplace) %{etc}/*
/etc/systemd/system/chaos-bonobo-server.service
%dir %{dest}
%{dest}/*
%dir /var/log/%{name}

#%license COPYING
#%doc ChangeLog README

%changelog
* Mon Nov 13 2023 Costis C. - 1.0.1
- Initial release

