import pandas as pd
from datetime import datetime
from pathlib import Path
from settings import BASE_DIR
import os
class ExportDataToCsv:
    def __init__(self,data_scan):
        self.data_scan = data_scan
        self.TODAY = datetime.today().strftime("%Y-%m-%d")
        self.df = pd.DataFrame.from_dict(self.data_scan,orient="index")
        self.kingdom = self.df.id_kingdom.unique()[0]
        self.extract_dir = os.path.join(BASE_DIR,"extract",str(self.kingdom),str(self.TODAY))
        os.makedirs(self.extract_dir,exist_ok=True)


    def export_to_csv(self):

        self.df.to_csv(f"{self.extract_dir}/scan_{datetime.today().strftime("%H_%M_%S")}.csv",sep=";",index=False)