
# BSD 3-Clause License

# Copyright (c) 2022, Marcus Behel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import traceback
from PySide2.QtWidgets import QMainWindow, QWidget, QMessageBox
from PySide2.QtCore import Signal, QStandardPaths
from PySide2.QtGui import QShowEvent, QCloseEvent
from typing import Optional
from ui_configwindow import Ui_ConfigWindow
from ui_config_list_item import Ui_ConfigListItem
import json
import os


class ConfigListItem(QWidget):
    removed = Signal(QWidget)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.ui = Ui_ConfigListItem()
        self.ui.setupUi(self)
        self.ui.btn_remove.clicked.connect(self.__remove)

    def __remove(self):
        self.removed.emit(self)


class ConfigWindow(QMainWindow):
    closed = Signal(dict)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.ui = Ui_ConfigWindow()
        self.ui.setupUi(self)
        self.list_items = []
        self.ui.btn_add.clicked.connect(self.add_config)
        self.cfg_file = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation) + "/config.json"

    def add_config(self):
        item = ConfigListItem()
        # Default args
        item.ui.txt_args.setPlainText("--dir-cache-time 1m0s\n--vfs-cache-mode full")
        item.removed.connect(self.remove_config)
        self.ui.sa_main.layout().insertWidget(self.ui.sa_main.layout().count() - 1, item)
        self.list_items.append(item)

    def remove_config(self, which: ConfigListItem):
        self.ui.sa_main.layout().removeWidget(which)
        self.list_items.remove(which)
        which.deleteLater()

    def clear_configs(self):
        for cfg_list_item in self.list_items:
            self.ui.sa_main.layout().removeWidget(cfg_list_item)
        self.list_items.clear()

    def show(self, data: dict):
        self.clear_configs()
        for i in range(data["count"]):
            self.add_config()
            obj: ConfigListItem = self.ui.sa_main.layout().itemAt(i).widget()
            obj.ui.txt_remote.setText(data["items"][str(i)]["remote_name"])
            obj.ui.txt_mountpoint.setText(data["items"][str(i)]["mount_point"])
            obj.ui.txt_args.setPlainText(data["items"][str(i)]["mount_args"])
        return super().show()
    
    def closeEvent(self, event: QCloseEvent):
        try:
            if not os.path.exists(os.path.dirname(self.cfg_file)):
                os.makedirs(os.path.dirname(self.cfg_file))
            with open(self.cfg_file, "w") as f:
                data = {}
                data["count"] = self.ui.sa_main.layout().count() - 1
                data["items"] = {}
                for i in range(data["count"]):
                    data["items"][str(i)] = {}
                    obj: ConfigListItem = self.ui.sa_main.layout().itemAt(i).widget()
                    data["items"][str(i)]["remote_name"] = obj.ui.txt_remote.text()
                    data["items"][str(i)]["mount_point"] = obj.ui.txt_mountpoint.text()
                    data["items"][str(i)]["mount_args"] = obj.ui.txt_args.toPlainText()
                json.dump(data, f)
                self.closed.emit(data)
        except Exception as e:
            traceback.print_exc()
            dialog = QMessageBox(self)
            dialog.setWindowTitle("RcloneDriveManager")
            dialog.setText("Error occurred saving configuration file.")
            dialog.setDetailedText("Exception '{}' occurred.".format(type(e).__name__))
            dialog.setIcon(QMessageBox.Warning)
            dialog.setStandardButtons(QMessageBox.Ok)
            dialog.setDefaultButton(QMessageBox.Ok)
            dialog.exec_()
            self.closed.emit({})
        return super().closeEvent(event)
