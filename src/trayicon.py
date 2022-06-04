
import shutil
import subprocess
import os
import json
import time
import traceback
from typing import Optional, List, Dict, Tuple
from PySide2.QtWidgets import QSystemTrayIcon, QMenu, QWidget, QApplication, QMessageBox, QAction
from PySide2.QtGui import QIcon
from PySide2.QtCore import QStandardPaths, QTimer
from configwindow import ConfigWindow


class TrayIcon(QSystemTrayIcon):
    def __init__(self, config_win: ConfigWindow, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.cfg_file = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation) + "/config.json"

        self.config_win = config_win
        self.menu = QMenu()
        self.setContextMenu(self.menu)
        self.poll_timer = QTimer(self)
        self.mounted_list: Dict[str, Tuple[str, subprocess.Popen]] = {} # name: (mountpoint, popen)
        self.mount_actions: List[QAction] = []
        self.data = {}
        self.data["count"] = 0
        self.data["items"] = {}
        self.construct_menu()
        self.setIcon(QIcon(":/icon.png"))
        self.setToolTip("RcloneDriveManager")

        if os.path.exists(self.cfg_file):
            try:
                with open(self.cfg_file, "r") as f:
                    data = json.load(f)
            except Exception as e:
                traceback.print_exc()
                dialog = QMessageBox()
                dialog.setWindowTitle("RcloneDriveManager")
                dialog.setText("Error occurred loading configuration file.")
                dialog.setDetailedText("{} occurred with message {}.".format(type(e).__name__, str(e)))
                dialog.setIcon(QMessageBox.Warning)
                dialog.setStandardButtons(QMessageBox.Ok)
                dialog.setDefaultButton(QMessageBox.Ok)
                dialog.exec_()
        self.update_menu(data)
        self.config_win.closed.connect(self.update_menu)
        self.poll_timer.timeout.connect(self.poll_mounted)
        self.poll_timer.setSingleShot(False)
        self.poll_timer.start(5000)

    def update_menu(self, data):
        for action in self.mount_actions:
            self.menu.removeAction(action)
            action.deleteLater()
        self.mount_actions.clear()
        self.data = data
        for i in range(self.data["count"]):
            name = self.data["items"][str(i)]["remote_name"]
            act = QAction(name, self.menu)
            act.setCheckable(True)
            act.setChecked(name in self.mounted_list)
            act.triggered.connect(self.toggle_mount)
            self.menu.insertAction(self.sep_2, act)
            self.mount_actions.append(act)

    def construct_menu(self):
        self.lbl_action = self.menu.addAction("RcloneDriveManager")
        self.sep_1 = self.menu.addSeparator()
        self.sep_2 = self.menu.addSeparator()
        self.quit_action = self.menu.addAction("Quit")
        self.quit_action.triggered.connect(self.exit_app)
        self.lbl_action.triggered.connect(self.open_config)
        self.setContextMenu(self.menu)

    def open_config(self):
        self.config_win.show(self.data)
    
    def act_for_name(self, name: str) -> QAction:
        for act in self.mount_actions:
            if act.text() == name:
                return act
        return None

    def poll_mounted(self):     
        to_delete = []  
        for name, value in self.mounted_list.items():
            proc = value[1]
            mountpoint = value[0]
            if proc.poll() is not None:
                to_delete.append(name)
                act = self.act_for_name(name)
                if act is not None:
                    act.setChecked(False)
                res = proc.poll()
                if res != 0:
                    dialog = QMessageBox()
                    dialog.setWindowTitle("RcloneDriveManager")
                    dialog.setText("Drive Unmounted Unexpectedly")
                    dialog.setDetailedText("Drive {} was unmounted unexpectedly. Rclone exited with code {}.".format(name, res))
                    dialog.setIcon(QMessageBox.Warning)
                    dialog.setStandardButtons(QMessageBox.Ok)
                    dialog.setDefaultButton(QMessageBox.Ok)
                    dialog.exec_()
                # Remove mount dir when unmounted (only if empty to prevent accidental data loss)
                try:
                    os.rmdir(mountpoint)
                except:
                    traceback.print_exc()
        for name in to_delete:
            del self.mounted_list[name]
    
    def toggle_mount(self):
        act: QAction = self.sender()
        name = act.text()
        if act.isChecked():
            # Don't actually check until mounted
            act.setChecked(False)
            self.mount(name)
        else:
            # Don't actually uncheck until unmounted
            act.setChecked(True)
            self.unmount(name)

    def mount(self, name: str):
        idx = -1
        for i in range(self.data["count"]):
            if self.data["items"][str(i)]["remote_name"] == name:
                idx = i
                break
        if idx == -1:
            dialog = QMessageBox()
            dialog.setWindowTitle("RcloneDriveManager")
            dialog.setText("Error occurred mounting the drive")
            dialog.setDetailedText("No configuration with the name {} was found.".format(name))
            dialog.setIcon(QMessageBox.Warning)
            dialog.setStandardButtons(QMessageBox.Ok)
            dialog.setDefaultButton(QMessageBox.Ok)
            dialog.exec_()
            return
        
        mountpoint = self.data["items"][str(idx)]["mount_point"]
        if mountpoint == "":
            dialog = QMessageBox()
            dialog.setWindowTitle("RcloneDriveManager")
            dialog.setText("Error occurred mounting the drive")
            dialog.setDetailedText("No mountpoint was specified.".format(name))
            dialog.setIcon(QMessageBox.Warning)
            dialog.setStandardButtons(QMessageBox.Ok)
            dialog.setDefaultButton(QMessageBox.Ok)
            dialog.exec_()
            return
        mountpoint = os.path.expandvars(os.path.expanduser(mountpoint))
        if not os.path.exists(mountpoint):
            os.makedirs(mountpoint)
        if not os.path.exists(mountpoint):
            dialog = QMessageBox()
            dialog.setWindowTitle("RcloneDriveManager")
            dialog.setText("Error occurred mounting the drive")
            dialog.setDetailedText("Mountpoint does not exist and could not be created.".format(name))
            dialog.setIcon(QMessageBox.Warning)
            dialog.setStandardButtons(QMessageBox.Ok)
            dialog.setDefaultButton(QMessageBox.Ok)
            dialog.exec_()
            return
        if not os.path.isdir(mountpoint):
            dialog = QMessageBox()
            dialog.setWindowTitle("RcloneDriveManager")
            dialog.setText("Error occurred mounting the drive")
            dialog.setDetailedText("Mountpoint exists, but is not a directory.".format(name))
            dialog.setIcon(QMessageBox.Warning)
            dialog.setStandardButtons(QMessageBox.Ok)
            dialog.setDefaultButton(QMessageBox.Ok)
            dialog.exec_()
            return
        if len(os.listdir(mountpoint)) != 0:
            dialog = QMessageBox()
            dialog.setWindowTitle("RcloneDriveManager")
            dialog.setText("Error occurred mounting the drive")
            dialog.setDetailedText("Mountpoint exists, but is a non-empty directory.".format(name))
            dialog.setIcon(QMessageBox.Warning)
            dialog.setStandardButtons(QMessageBox.Ok)
            dialog.setDefaultButton(QMessageBox.Ok)
            dialog.exec_()
            return

        # TODO subprocess call rclone to mount
        # Also need to make mount directory first if it does not exit
        # Also, error if mount directory not empty
        # store popen for later
        user_args = str(self.data["items"][str(idx)]["mount_args"]).split()
        args = []
        args.append("rclone")
        args.append("mount")
        args.extend(user_args)
        args.append("{}:/".format(name)),
        args.append("{}".format(mountpoint))

        print(" ".join(args))
        p = subprocess.Popen(args)

        # Show mount failed if process dies immediately (within 100ms)
        start = time.time()
        while time.time() - start < 0.1:
            if p.poll() is not None:
                res = p.poll()
                dialog = QMessageBox()
                dialog.setWindowTitle("RcloneDriveManager")
                dialog.setText("Error occurred mounting the drive")
                dialog.setDetailedText("Rclone exited with error code {}.".format(res))
                dialog.setIcon(QMessageBox.Warning)
                dialog.setStandardButtons(QMessageBox.Ok)
                dialog.setDefaultButton(QMessageBox.Ok)
                dialog.exec_()
                return
            time.sleep(0.01)

        self.mounted_list[name] = (mountpoint, p)

        act = self.act_for_name(name)
        if act is not None:
            act.setChecked(True)

    def unmount(self, name: str, force: bool = False, noprompt: bool = False):
        # Don't check this process in poll_mounted anymore
        proc = self.mounted_list[name][1]
        mountpoint = self.mounted_list[name][0]
        del self.mounted_list[name]
        
        # If process is already dead, just remove checkmark
        if proc.poll() is not None:
            act = self.act_for_name(name)
            if act is not None:
                act.setChecked(False)
            return

        # Try clean unmount
        # Try up to 3 times with 100ms delay between
        for i in range(3):
            res = subprocess.call(["umount", mountpoint])
            if res == 0:
                break
            time.sleep(0.1)

        # Force unmount by killing rclone if clean unmount failed
        if res != 0:
            if force:
                proc.terminate()
                start = time.time()
                while (time.time() - start < 0.3) and (proc.poll() is None):
                    time.sleep(0.01)
                if proc.poll() is None:
                    proc.kill()
            else:
                # Unmount failed. Add back to list
                self.mounted_list[name] = (mountpoint, proc)
                if not noprompt:
                    dialog = QMessageBox()
                    dialog.setWindowTitle("RcloneDriveManager")
                    dialog.setText("Unmount failed")
                    dialog.setDetailedText("Failed to cleanly unmount {}.".format(name))
                    dialog.setIcon(QMessageBox.Warning)
                    dialog.setStandardButtons(QMessageBox.Ok)
                    dialog.setDefaultButton(QMessageBox.Ok)
                    dialog.exec_()
                return False
        
        # Remove mount dir when unmounted (only if empty to prevent accidental data loss)
        try:
            os.rmdir(mountpoint)
        except:
            traceback.print_exc()

        act = self.act_for_name(name)
        if act is not None:
            act.setChecked(False)
        return True
        


    def exit_app(self):
        dialog = QMessageBox()
        dialog.setWindowTitle("RcloneDriveManager")
        dialog.setText("Are you sure you want to quit? QUITTING WILL UNMOUNT ALL DRIVES!")
        dialog.setIcon(QMessageBox.Question)
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dialog.setDefaultButton(QMessageBox.No)
        res = dialog.exec_()
        if res == QMessageBox.Yes:
            # Unmount all
            self.poll_timer.stop()
            for name, value in self.mounted_list.copy().items():
                if not self.unmount(name, False, True):
                    dialog = QMessageBox()
                    dialog.setWindowTitle("RcloneDriveManager")
                    dialog.setText("Failed to cleanly umount {}. Force unmount? If no is selected, the application will not exit.".format(name))
                    dialog.setIcon(QMessageBox.Question)
                    dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    dialog.setDefaultButton(QMessageBox.No)
                    res = dialog.exec_()
                    if res != QMessageBox.Yes:
                         # Exit was aborted. Restart poll timer
                        self.poll_timer.start(5000)
                        return
                    # Force unmount
                    self.unmount(name, True, True)
            QApplication.instance().quit()
            
           

