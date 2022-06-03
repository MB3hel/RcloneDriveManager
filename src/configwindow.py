
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
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.ui = Ui_ConfigWindow()
        self.ui.setupUi(self)
        self.ui.btn_add.clicked.connect(self.add_config)
        self.cfg_file = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation) + "/config.json"

    def add_config(self):
        item = ConfigListItem()
        item.removed.connect(self.remove_config)
        self.ui.sa_main.layout().insertWidget(self.ui.sa_main.layout().count() - 1, item)

    def remove_config(self, which: ConfigListItem):
        self.ui.sa_main.layout().removeWidget(which)
        which.deleteLater()
    
    def showEvent(self, event: QShowEvent):
        if os.path.exists(self.cfg_file):
            try:
                with open(self.cfg_file, "r") as f:
                    data = json.load(f)
                    count = data["count"]
                    for i in range(count):
                        self.add_config()
                        obj: ConfigListItem = self.ui.sa_main.layout().itemAt(i).widget()
                        obj.ui.txt_remote.setText(data["items"][str(i)]["remote_name"])
                        obj.ui.txt_mountpoint.setText(data["items"][str(i)]["mount_point"])
                        obj.ui.txt_args.setPlainText(data["items"][str(i)]["mount_args"])
            except Exception as e:
                traceback.print_exc()
                dialog = QMessageBox(self)
                dialog.setWindowTitle("Error loading config.")
                dialog.setText("Exception '{}' occurred.".format(type(e).__name__))
                dialog.setIcon(QMessageBox.Warning)
                dialog.setStandardButtons(QMessageBox.Ok)
                dialog.setDefaultButton(QMessageBox.Ok)
                dialog.exec_()
        return super().showEvent(event)
    
    def closeEvent(self, event: QCloseEvent):
        try:
            if not os.path.exists(os.path.dirname(self.cfg_file)):
                os.makedirs(os.path.dirname(self.cfg_file))
            with open(self.cfg_file, "w") as f:
                data = {}
                data["count"] = self.ui.sa_main.layout().count() - 1
                data["items"] = {}
                for i in range(data["count"]):
                    data["items"][i] = {}
                    obj: ConfigListItem = self.ui.sa_main.layout().itemAt(i).widget()
                    data["items"][i]["remote_name"] = obj.ui.txt_remote.text()
                    data["items"][i]["mount_point"] = obj.ui.txt_mountpoint.text()
                    data["items"][i]["mount_args"] = obj.ui.txt_args.toPlainText()
                json.dump(data, f)
        except Exception as e:
            traceback.print_exc()
            dialog = QMessageBox(self)
            dialog.setWindowTitle("Error saving config.")
            dialog.setText("Exception '{}' occurred.".format(type(e).__name__))
            dialog.setIcon(QMessageBox.Warning)
            dialog.setStandardButtons(QMessageBox.Ok)
            dialog.setDefaultButton(QMessageBox.Ok)
            dialog.exec_()
        return super().closeEvent(event)
