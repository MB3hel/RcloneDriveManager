Name:       rclone-drive-manager
Version:    1.0.3
Release:    1
Summary:    Tray icon to mount / unmount rclone remotes.
License:    BSD-3-Clause
Requires:   rclone, python3, python3-pyside6

%description
Tray icon to mount / unmount rclone remotes.

%prep

%build

%install
echo %{_pkg_build_dir}
cp -a %{_pkg_build_dir}/* %{buildroot}/

%files
/usr/lib/*
/usr/share/applications/*
/usr/share/doc/*

