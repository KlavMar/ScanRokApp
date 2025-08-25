
import logging
import sys
from pathlib import Path
from datetime import datetime
from settings import BASE_DIR
import os,sys
def setup_logger(level: int = logging.INFO):
    """
    Configure un logger global pour toute l'application.
    """

    today =datetime.today().strftime("%Y-%m-%d")


    # Format commun
    log_format = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Handler console (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))

    pathlog = os.path.join(BASE_DIR,"logs", today)
    os.makedirs(pathlog,exist_ok=True)
    file_handler=logging.FileHandler(f"{pathlog}/logging.log",encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(log_format, date_format))

    # Logger racine
    logging.basicConfig(
        level=level,
        handlers=[console_handler, file_handler]
    )

    logging.debug("Logger initialisé")
