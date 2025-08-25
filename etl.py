import pandas as pd
import datetime
import re
        
list_civ=['Greece',
 'Rome',
 'Germany',
 'Britain',
 'France',
 'China',
 'Vikings',
 'Egypt',
 'Japan',
 'Korea',
 'Spain',
 'Arabia',
 'Ottoman Empire',
 'Byzantium',
 'N/A']
today = datetime.datetime.now().date()

def etl_data(path_file,df_=False,*args,**kwargs):
   
    if df_ == False:
        df = pd.read_csv(path_file,sep=";",index_col=0)
    else:
        df=path_file
    

    today = datetime.datetime.now().date()

    df["scan_alliance"] = df.alliance

    df.alliance=df.alliance.str.replace(r"\(","[",regex=True)
    df.alliance=df.alliance.str.replace(r"\\n","",regex=True)
    df.alliance=df.alliance.str.replace(r"\)","]",regex=True)
    df.alliance=df.alliance.str.replace("|".join(["!","~","_"]),"",regex=True)

    today_str = today.strftime('%Y-%m-%d')

    df["date"]=today_str
    df.date = pd.to_datetime(df.date,format="%Y-%m-%d")
    pattern = r"(?!.*])([\w\s]*)"
    pattern_tags=r"(\[[\w\-\_]*\])"
    df['alliance'] = df['alliance'].astype(str)
    df=df.fillna(0)
    try:
        df.power=df.power.apply(lambda x:re.findall(r"([\d]+)",x)[0])
    except:
        pass
    df["tags"]=df.alliance.apply(lambda x:"".join(re.findall(pattern_tags,x)))
    df["name_alliance"]=df.alliance.apply(lambda x:"".join(re.findall(pattern,x)))
    df.name_alliance = df.name_alliance.str.lower().str.replace("\\n","",regex=True)
    
    df["civilisation"]=df["civilisation"].str.strip().str.lower()

    pattern="([A-Za-z]*)"
   
    df.civilisation=df.civilisation.astype("str")
    df.civilisation = df.civilisation.apply(lambda x:" ".join(re.findall(pattern,x)))



    for name_civ in list_civ:
        df.loc[df.civilisation.str.contains(name_civ,regex=False,case=False),"civilisation_"]=name_civ

    #df.loc[~df.civilisation.str.contains("|".join(list_civ),regex=False,case=False),"civilisation"]="NaN"
    df=df.drop(["alliance","civilisation"],axis=1)
    df=df.rename(columns={"civilisation_":"civilisation"})
    df.civilisation=df.civilisation.str.capitalize()

    df=df.drop_duplicates("governor_id")
    
    return df 

      

  