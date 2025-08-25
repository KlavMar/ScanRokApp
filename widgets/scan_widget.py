# tab1explorer.py

import logging
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit,QHBoxLayout,  
                             QVBoxLayout,QTabWidget, QWidget, QGridLayout, 
                             QLabel, QPushButton, QCheckBox,QComboBox,
                             QLineEdit,QSizePolicy,QWidgetAction)
from PyQt6.QtCore import QTimer,QProcess,pyqtSignal,QThread,QTimer, QIODevice, QFile,QObject,QUrl
import threading
import configparser
import os,sys
from cores.process_scan import scan
from utils.file_manager import ExportDataToCsv

class ScanThread(QThread):
    scan_finish = pyqtSignal()
    def __init__(self,players,start_scan,power_min):
          super().__init__()
         # self.kingdom = kingdom
          self.players = players
          self.start_scan =start_scan
          self.power_min = power_min
    def run(self):
        data = scan(nb_scan=self.players,start = self.start_scan,power_min=self.power_min)
        ExportDataToCsv(data_scan = data).export_to_csv()
        self.scan_finish.emit()


class LogHandler(QObject, logging.Handler):
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        logging.Handler.__init__(self)

    def emit(self, record):
        log_entry = self.format(record)
        self.log_signal.emit(log_entry)

class TabScan(QWidget):
    def __init__(self):
        super().__init__()

        # Créer le layout principal
        layout = QGridLayout()

        # Champ pour choisir le royaume

        form_layout = QVBoxLayout()

        self.kingdom_choose = QLineEdit()
        form_layout.addWidget(QLabel("Kingdom detect automatic while scan")) # line column
        #form_layout.addWidget(self.kingdom_choose)

        # Champ pour le numéro de départ
        form_layout.addWidget(QLabel("N° start " ))
        form_layout.addWidget(QLabel("you need to scroll to n° start before start scan"))
        self.num_start = QLineEdit()
        self.num_start.setText("1")
        form_layout.addWidget(self.num_start)

        # Power min scan 
        form_layout.addWidget(QLabel("Power min scan"))
        self.power_min = QLineEdit()
        form_layout.addWidget(self.power_min)
        # Champ pour le nombre de joueurs

        
        form_layout.addWidget(QLabel("Select number of players"))
        self.players_number = QLineEdit()  # Ou utilisez QComboBox si nécessaire
        form_layout.addWidget(self.players_number)
        

        

        layout.addLayout(form_layout, 1, 0)

        # Boutons pour lancer le script et fermer BlueStacks
        self.btn_start_script = QPushButton("Start scan")
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_start_script)
      #  button_layout.addWidget(self.btn_close_app)

        layout.addLayout(button_layout, 2, 0)
        # Configuration de la zone de texte pour les logs
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.text_edit, 3,0, 3, 4)  # Ligne 0 à 3, colonne 2 (4 lignes de hauteur)



        # Gestionnaire de logs
        self.log_handler = LogHandler()
        self.log_handler.log_signal.connect(self.append_log)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s -  %(message)s')
        self.log_handler.setFormatter(formatter)
        logging.getLogger().addHandler(self.log_handler)
       # logging.getLogger().setLevel(logging.DEBUG)

        self.btn_start_script.clicked.connect(self.params)


        # Appliquer le layout au widget
        self.setLayout(layout)

    def append_log(self, message):
        self.text_edit.append(message)


    def params(self):
    
       # kingdom = int(self.kingdom_choose.text())
        players = int(self.players_number.text()) if self.players_number.text() else None
        power_min = int(self.power_min.text()) if self.power_min.text() else None
        start_scan = int(self.num_start.text())
        self.scan_thread = ScanThread(players,start_scan,power_min=power_min)

        self.scan_thread.start()


    
# Méthode pour démarrer le thread de scan
    def start_scan_thread(self):
        self.scan_thread.start()

