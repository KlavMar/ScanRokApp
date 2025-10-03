import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import datetime as dt
import re
import urllib.parse
from pathlib import Path
from sqlalchemy import create_engine
import requests
import sys

# Classe de connexion à la base de données
class ConnectionDb:
    def __init__(self, host, port, user, password, db):
        self.host = host
        self.user = user
        self.port = port
        self.password = password
        self.db = db
    
    def parse_password(self):
        # Encodage du mot de passe pour utilisation dans l'URL de connexion SQL
        pattern = "([\w]*[#@$][\w]*)"
        if re.match(pattern, self.password):
            mdp = urllib.parse.quote_plus(self.password)
        else:
            mdp = self.password
        return mdp
    

class ConnectionPostgreSQL(ConnectionDb):
    def __init__(self, host, port, user, password, db):
        super().__init__(host, port, user, password, db)

    def get_sql_engine(self):
        mdp = super().parse_password()
        sqlEngine = create_engine(
            f'postgresql://{self.user}:{mdp}@{self.host}:{self.port}/{self.db}',
            pool_recycle=1200
        )
        return sqlEngine

    def get_connection(self):
        sqlEngine = self.get_sql_engine()
        return sqlEngine.connect()

    def get_close(self):
        connection = self.get_connection()
        return connection.close()