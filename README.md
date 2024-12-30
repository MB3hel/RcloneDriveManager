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

- Change version if needed in `res/version.txt` and `packaging/deb_control`

```sh
python compile.py
cd packagaing
./ubuntu.sh
```

## GUI Config file example

*Can configure via gui, but file can be backed up / copied as needed.*

`~/.local/share/rclone-drive-manager/config.json`

```
{
    "count": 1, 
    "items": {
        "0": {
            "remote_name": "OneDrive", 
            "mount_point": "~/OneDrive", 
            "mount_args": "--vfs-cache-mode writes"
        }
    }
}
```

Note that remotes must be setup in rclone. The GUI config just determines what pre-setup remote name to mount and how / where.
