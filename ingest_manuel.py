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
            pool_recycle=1200,#echo=True
        )
        return sqlEngine

    def get_connection(self):
        sqlEngine = self.get_sql_engine()
        return sqlEngine.connect()

    def get_close(self):
        connection = self.get_connection()
        return connection.close()

# Fonction de traitement du CSV vers la base de données SQL
def traitement_csv_to_sql(path_file, df_=False):
    today = dt.datetime.now().date()
    # Lecture du fichier CSV
    if not df_:
        df = pd.read_csv(path_file, sep=";")

    else:
        df = path_file
    try:
        df.name_alliance =df.name_alliance.apply(lambda x:np.nan if re.match(r"(^[\d]+$)",str(x)) else x)
    except:
        print("ici")
        today_str = today.strftime('%Y-%m-%d')

        df["date"]=today_str
        df.date = pd.to_datetime(df.date,format="%Y-%m-%d")
        pattern = r"(?!.*])([\w\s]*)"
        pattern_tags=r"(\[[\w\-\_]*\])"
        df["tags"]=df.alliance.apply(lambda x:"".join(re.findall(pattern_tags,x)))
        df["name_alliance"]=df.alliance.apply(lambda x:"".join(re.findall(pattern,x)))
        df.name_alliance =df.name_alliance.apply(lambda x:np.nan if re.match(r"(^[\d]+$)",str(x)) else x)
        print(df.columns)
        df=df.drop(["alliance"],axis=1)

    # Transformation des colonnes KILLS
    for col in df.filter(regex="kills"):
        df[col] = df[col].astype("str").str.replace("\n", "0").astype("float")
    
    # Ajout de la date d'aujourd'hui au DataFrame
    #today_str = datetime.now().date().strftime('%Y-%m-%d')
    #df["date"] = pd.to_datetime(today_str, format="%Y-%m-%d")

    df = df.drop_duplicates("governor_id")
    
    return df

def main(kvk=True):
    # Paramètres de connexion
    if sys.argv[1]:
        delta = int(sys.argv[1])
        print(f"delta {delta}")
    #db_conn = ConnectionPostgreSQL("192.168.1.10", "7000", "your_username", "your_password", "your_database")
    #db_conn = ConnectionMySQL("192.168.1.10", "3306", "ArzRtDb", "6Arzi@2Kival9@", "rok")
    db_conn = ConnectionPostgreSQL("192.168.1.10", "7000", "Arzpost", "6Arzi2Kival9", "platform_db")
    db = db_conn.get_connection()
    db.rollback()
    # Chemin du répertoire principal
    base_path = Path(os.path.join(os.path.expanduser("~"), "Desktop", "scan", "extract"))
    kingdoms = os.listdir(base_path)
 
    today = datetime.now().date() -timedelta(days=delta)
    today = today.strftime("%Y-%m-%d")
    print(f"Date insert {today}")
    #print(pd.read_sql_query("SELECT * FROM rise_scandata LIMIT 1",db))
    # Initialisation du DataFrame pour stocker les données concaténées
    df = pd.DataFrame()

    # Parcours des fichiers CSV du jour pour les concaténer
    for kingdom in kingdoms:
        if re.match("[\d]+",kingdom):
            if  int(kingdom) != 9999:
                for date_dir in os.listdir(os.path.join(base_path, kingdom)):
                    if date_dir == today:
                        print(kingdom)
                        for file in os.listdir(os.path.join(base_path, kingdom, date_dir)):
                            if file.endswith(".csv"):
                                path_file = os.path.join(base_path, kingdom, date_dir, file)
                                # Lecture du fichier CSV et concaténation avec le DataFrame
                                df = pd.concat([df, pd.read_csv(path_file, sep=";")], ignore_index=True)

    # Traitement du DataFrame et préparation pour l'insertion SQL
    df["date"] = pd.to_datetime(today, format="%Y-%m-%d")
    df = traitement_csv_to_sql(df,df_=True)
    #df = df.rename(columns={"id_kingdom": "id_kingdom_id"})
    df  = df.rename(columns={"tags":"tags_alliance","civilisation":"name_civilisation"})


    kvk = sys.argv[2].lower() == "true"

    
    try: 
        kingdom_filter = int(sys.argv[3])
    except :
        kingdom_filter = None
   
    try:
        df = df.fillna(0)
        # Insertion dans la table `rise_scandata`
        #df.loc[df.id_kingdom==1165].to_sql('rise_rawscandata', db, if_exists="append", index=False)
        print(df.head())
        df.columns = df.columns.str.lower()
        #if kingdom_filter is None:
            
          #  df.loc[(df.id_kingdom==1165) & (df.power>=1000000)].to_sql('scan_rawscandata', db, if_exists="append",schema="cores_services",index=False)

        if kvk == True:
            q = "SELECT id_kvk FROM cores_services.kvk_kvkdate ORDER BY date_begin DESC LIMIT 1"

            df_kvk = pd.read_sql_query(q,con=db)
            df["id_kvk_id"] =int(df_kvk.id_kvk.values[0])
            print(df.head())

            if kingdom_filter:
                df =df[df.id_kingdom == kingdom_filter]
            #df.to_sql('scan_rawscancamp', db, if_exists="append", schema="cores_services",index=False)
            # nombre de lignes avant
            count_before = pd.read_sql("SELECT COUNT(*) FROM cores_services.scan_rawscancamp;", db).iloc[0,0]

            # insertion
            engine = db_conn.get_sql_engine()

            with engine.begin() as connection:
                df.to_sql(
                    'scan_rawscancamp',
                    connection,
                    if_exists="append",
                    schema="cores_services",
                    index=False
                )

            # nombre de lignes après
            count_after = pd.read_sql("SELECT COUNT(*) FROM cores_services.scan_rawscancamp;", db).iloc[0,0]

            print(f"Lignes avant : {count_before}, après : {count_after}")
            print(f"{count_after - count_before} nouvelles lignes insérées ✅")
            
                
        #df.to_excel('rise_rawscandata.xlsx',index=False)
        print("Les données ont été traitées et insérées dans la base de données avec succès.")

    except Exception as e:
        print(e)
    
    finally:
        res = requests.post("https://webapp.arzibot.com/dbt/dbt-run/")
        print(res.status_code)
        
    db_conn.get_close()
if __name__ == "__main__":
    main()