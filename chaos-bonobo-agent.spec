#
# spec file for package chaos-bonobo-agent
#
#

Name:           chaos-bonobo-agent
Version:        %{_version}
Release:        %{_release}
Summary:        The Chaos-Bonobo Agent
License:        Apache
Packager:       CostisC
BuildArch:      noarch
Requires:       python(abi)     >= 3.6

%global dest /usr/share/%{name}
%global etc /etc/chaos-bonobo

%description
The Agent counterpart of the Chaos Bonobo framework.
Quick instructions:
* Read the documentation on running server (e.g. http://<address>:4440/docs)



%install
mkdir -p %{buildroot}%{dest} %{buildroot}%{etc}
mkdir -p %{buildroot}/etc/systemd/system/
mkdir -p %{buildroot}/var/log/%{name}
cp -a bonobo-agent.py experiments/  %{buildroot}%{dest}
cp agent.conf id_script.sh %{buildroot}%{etc}
cp chaos-bonobo-agent.service /%{buildroot}/etc/systemd/system/


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
/etc/systemd/system/chaos-bonobo-agent.service
%dir %{dest}
%attr(0744, -, -) %{dest}/bonobo-agent.py
%{dest}/*
%dir /var/log/%{name}

#%license COPYING
#%doc ChangeLog README

%changelog
* Mon Nov 13 2023 Costis C. - 1.0.1
- Initial release

