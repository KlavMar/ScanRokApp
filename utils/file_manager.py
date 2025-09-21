import pandas as pd
from datetime import datetime
from pathlib import Path
from settings import BASE_DIR
import os
class ExportData:
    def __init__(self,el):

        self.TODAY = datetime.today().strftime("%Y-%m-%d")
       # self.data = el.get("data")

        
        self.kingdom = el.get("kingdom")
        self.extract_dir = os.path.join(BASE_DIR,"extract",str(self.kingdom),str(self.TODAY))
        self.date = el.get("time_created")
        self.create_dir()
        self.name = f"{self.extract_dir}/scan_{self.date}"

        self.filename_json = f'backup_{self.date}.ndjson'
        self.df  = self.create_df()
    
    def create_dir(self):
        return os.makedirs(self.extract_dir,exist_ok=True)
    def create_df(self):
        path_ = Path(self.extract_dir) / self.filename_json
        df = pd.read_json(path_, lines=True)
        return df 

    def export_to_csv(self):

        self.df.to_csv(f"{self.name}.csv",sep=";",index=False)

    def export_to_excel(self):
        self.df.to_excel(f"{self.name}.xlsx",index=False)