from datetime import datetime, timedelta
import datetime as dt
import pandas as pd 
import numpy as np
import re
def traitement_csv_to_sql(path_file, db, df_=False):
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