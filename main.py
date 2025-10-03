import sys
from PyQt6.QtWidgets import QApplication, QWidget
from logger_config import setup_logger
import logging
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit,
                             QTabWidget, QWidget, QGridLayout, QVBoxLayout,QLabel, QPushButton, 
                             QCheckBox,QComboBox,QLineEdit,QSizePolicy,QWidgetAction)
from qt_material import apply_stylesheet,list_themes
import subprocess
import signal
import pandas as pd 
import os
from PyQt6.QtCore import Qt,QProcess,pyqtSignal,QThread,QTimer, QIODevice, QFile,QObject,QUrl
from PyQt6.QtGui import QTextCursor,QAction
from settings import BASE_DIR,load_qss
from pathlib import Path
from widgets.scan_widget import TabScan
from widgets.settings_widget import TabSettings
from api_services.token_validator import gatekeeper_or_exit
from cores.storage import StorageSqlite
import threading

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)

        self.setWindowTitle("Scan Kingdom")
        self.setGeometry(200,100,1200,900)

        tab_widget = QTabWidget()
        self.setCentralWidget(tab_widget)

        tab_widget.addTab(TabScan(),"Scan")
        tab_widget.addTab(TabSettings(),"Settings")




if __name__ == "__main__":
    setup_logger(level=logging.INFO)
    StorageSqlite().init_bdd()
    app = QApplication(sys.argv)
  #  token = gatekeeper_or_exit()
    qss = load_qss(os.path.join(BASE_DIR,"styles","theme.qss"),)   # ton ancien thème
    app.setStyleSheet(qss)  # ← un seul setStyleSheet
    win = MainWindow()
    win.show()


    sys.exit(app.exec())
