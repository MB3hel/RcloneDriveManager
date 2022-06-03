import sys

from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt

from configwindow import ConfigWindow


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setApplicationName("rclone-drive-manager")
    win = ConfigWindow()
    win.show()
    app.exec_()