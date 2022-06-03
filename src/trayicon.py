
import os
import json
import traceback
from typing import Optional, List, Dict
from PySide2.QtWidgets import QSystemTrayIcon, QMenu, QWidget, QApplication, QMessageBox, QAction
from PySide2.QtGui import QIcon
from PySide2.QtCore import QStandardPaths
from configwindow import ConfigWindow


class TrayIcon(QSystemTrayIcon):
    def __init__(self, config_win: ConfigWindow, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.cfg_file = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation) + "/config.json"

        self.config_win = config_win
        self.menu = QMenu()
        self.setContextMenu(self.menu)
        self.mounted_list: Dict[str, str] = []
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

    def poll_mounted(self):
        # TODO: Check all currently mounted to make sure they are still mounted
        # If not remove from list
        pass
    
    def mount(self, name: str):
        # TODO: Mount
        pass

    def unmount(self, name: str):
        # TODO: Unmount
        pass

    def exit_app(self):
        # TODO: Prompt user first
        # TODO: Unmount all if mounted
        QApplication.instance().quit()
