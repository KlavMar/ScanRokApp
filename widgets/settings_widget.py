# tab1explorer.py

import logging
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit,QHBoxLayout,  
                             QVBoxLayout,QTabWidget, QWidget, QGridLayout, 
                             QLabel, QPushButton, QCheckBox,QComboBox,QTableWidget,QTableWidgetItem,
                             QLineEdit,QSizePolicy,QWidgetAction)
from PyQt6.QtCore import QTimer,QProcess,pyqtSignal,QThread,QTimer, QIODevice, QFile,QObject,QUrl
from cores.storage import StorageSqlite


class TabSettings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        root = QGridLayout(self)            
        vbox = QVBoxLayout()               
        
        rows = StorageSqlite().load(q="SELECT token,expires_at,date_validated FROM tokens ORDER BY id DESC")
        table = QTableWidget()
        table.setRowCount(len(rows))
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["token","expires_at","date_validated"])

        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(str(value)))

        vboxform = QVBoxLayout()
        vboxform.addWidget(QLabel("Your Kingdom"))
        self.kindgom = vboxform.addWidget(QLineEdit())
        vbox.addWidget(table)
        root.addLayout(vboxform,0,0)
        root.addLayout(vbox, 1, 0)
