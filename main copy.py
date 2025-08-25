from cores.process_scan import scan
from utils.file_manager import ExportDataToCsv
from datetime import datetime
import os,sys
import logging
from logger_config import setup_logger


kingdom = 1165
nb_scan = 10
IMG_DIR = "img"
os.makedirs(IMG_DIR,exist_ok=True)
EXTRACT_DIR = "extract"
TODAY = datetime.today().strftime("%Y-%m-%d")
extract_dir_kingdom =os.path.join(EXTRACT_DIR,str(kingdom),TODAY)
os.makedirs(extract_dir_kingdom,exist_ok=True)

data = scan(kingdom,nb_scan,1)
ExportDataToCsv(data_scan = data,extract_dir=extract_dir_kingdom).export_to_csv()