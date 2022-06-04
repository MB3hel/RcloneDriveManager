# RcloneDriveManager

Simple app to mount / unmount rclone remote drives using a system tray icon.

Designed for / tested on / probably only works on Linux systems.

## Development Setup & Running

```sh
python3 -m venv env
source env/bin/activate
python -m pip install -U PySide2
python src/main.py
```

## Packaging and Running

```sh
python compile.py
cd packagaing
./ubuntu.sh
```
