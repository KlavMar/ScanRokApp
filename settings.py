import os,sys
from pathlib import Path
def get_default_path():
    if getattr(sys, 'frozen', False):  
        base_path = sys._MEIPASS
    else:
        base_path = os.getcwd()
    return base_path

BASE_DIR = get_default_path()

def load_qss(*files) -> str:
    chunks = []
    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            chunks.append(fh.read())
    return "\n".join(chunks)

def resource_path(*parts):
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return str(Path(base, *parts))