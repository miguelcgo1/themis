Name:           themis
Version:        1.0.0
Release:        1%{?dist}
Summary:        Themis - Window management for Linux, based on Rectangle for macOS

License:        MIT
URL:            https://github.com/miguel/themis
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

Requires:       python3
Requires:       python3-gobject
Requires:       python3-cairo
Requires:       python3-xlib
Requires:       python3-pynput
Requires:       libwnck3
Requires:       libappindicator-gtk3

%description
Themis is a window management application for Linux, inspired by and based 
on Rectangle for macOS. This is a specialized Linux version of Rectangle 
that works across all distributions including Fedora, providing powerful 
window management functionality.

Features:
- Window snapping with keyboard shortcuts
- Drag-to-snap functionality
- Support for X11 and Wayland
- Cross-distribution compatibility
- Customizable keyboard shortcuts
- Quarter, half, and third window positioning

%prep
%autosetup -n %{name}-%{version}

%build
%py3_build

%install
%py3_install

%files
%doc README.md
%license LICENSE
%{python3_sitelib}/*
%{_bindir}/themis
%{_datadir}/applications/themis.desktop
%{_datadir}/pixmaps/themis.png

%changelog
* Wed Aug 14 2025 Miguel Gomes <miguel@example.com> - 1.0.0-1
- Initial package