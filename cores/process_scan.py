
from datetime import datetime,timedelta
import time
import pyperclip
from utils.scan_manager import CoordScanOcrPlayers,CoordsGamesInteraction
from utils.image_manager import TreatmentScreenshotControlManager,Timage
import logging
from utils.treatment import GetValueImageScan,GetDataImageRoi
import threading
import pandas as pd
from cores.process_get_kd import ProcessGetKd
import sys,os
from utils.bluestack_manager import BluestackDeviceManager
import json
from settings import BASE_DIR
from utils.file_manager import ExportData

logger = logging.getLogger(__name__)    

def scan_get_devices():
    manager = BluestackDeviceManager(port=5037)  
    logger.info(manager.get_connect(port=5555))
    devices = manager.get_devices()

    if not devices:
        logger.info("Aucun device détecté")
        exit()

    device = devices[0]
    logger.info("Device connecté :%s" ,device)
    return device

def scan(nb_scan:int=None,start:int=None,power_min:int=None,device=None)->dict:
    start_created = datetime.today().strftime("%H_%M_%S")
    Y=285
    start_time_scan= time.time() 

    min_power = power_min if power_min else 1000000
    nb_scan = nb_scan if nb_scan else 300
    coords_in_game = CoordsGamesInteraction()
    if device is None:
        device = scan_get_devices()

    data_scan = dict()
    kwargs = {"inversed":False, "gray":True}

    # --- Récupère kingdom ---
    kingdom = ProcessGetKd(device=device).get_kingdom_by_image(**kwargs)

    device.shell("input tap 377 33") 
    time.sleep(5.0)
    pyperclip.copy("")
    time.sleep(1.0)
    device.shell(coords_in_game.open_gov)
    logger.info("open gov")
    time.sleep(1.0)
    device.shell(coords_in_game.open_ranking_menu)
    logger.info("open ranking")
    time.sleep(1.0)
    device.shell(coords_in_game.open_ranking_power)
    logger.info("open ranking power")
    time.sleep(1.0)

    last_power = 10*10**10 
    governor_name_previous = ""
    index_range_ppl = 0

    while min_power < last_power:

        if index_range_ppl > nb_scan:
            break

        logger.info(f"min:{min_power} last:{last_power}")
        logger.info(index_range_ppl+1)
        start_time_scan_each = time.time()

        k = 585 if index_range_ppl >= 4 or start >= 4 else Y + (index_range_ppl * 100)
        input_open_gov = f'input tap 280 {k}'
        data = dict() 
        threads  = list()

        object_gov = CoordScanOcrPlayers()
        filenames = {
            "gov_info": object_gov.get_gov_info(),
            "kills_tier": object_gov.get_tiers_kill(),
            "more_info": object_gov.get_more_info()
        }

        dict_value_img = {
            "gov_info": (600, 84, 450, 40),
            "more_info": (690,37,250,40),
            "kills_tier": (1070,330,200,40)
        }
        kwargs = {"index_k":k}

        # --- Capture & contrôle ---
        ram_images = {}  # stocke les images RAM par filename
        for filename in filenames.keys():
            if filename == "gov_info":
                coords = [input_open_gov]
            elif filename == "kills_tier":
                coords = [coords_in_game.input_open_kill_tiers]
            elif filename == "more_info":
                coords = [coords_in_game.input_open_more_info,
                          coords_in_game.input_close_more_info]

            control_image = TreatmentScreenshotControlManager(
                device=device,
                filename=filename,
                coord=coords,
                roi=dict_value_img.get(filename),
            )
            control_image.screenshot_get_data(**kwargs)
            ram_images[filename] = control_image.last_image  # garde l’image RAM

            if filename == "gov_info":
                roi_gov_id = object_gov.get_governor_id()
                treatment_gov  = GetDataImageRoi(
                    device=device,
                    image=ram_images[filename],
                    name=filename,
                    data=data,
                    roi=roi_gov_id,
                    index=0,
                    kwargs=kwargs
                )
                governor_id,id_kingdom = treatment_gov.get_governor_id_kd()

                roi_gov_name = object_gov.get_governor_name()
                governor_name = GetValueImageScan(
                    device=device,
                    image=ram_images[filename],
                    name=filename,
                    data=data,
                    roi=roi_gov_name,
                    index=0
                ).get_governor_name()

                data.update({
                    "governor_id": governor_id,
                    "id_kingdom": id_kingdom if id_kingdom else kingdom,
                    "governor_name": governor_name
                })
                governor_name_previous = governor_name
                kwargs.update({"governor_name_previous": governor_name_previous})

        # --- OCR des autres données en parallèle ---
        for filename, el in filenames.items():
            img = ram_images.get(filename)
            if img is None:  # fallback disque si RAM vide
                logger.warning(f"Aucune image RAM dispo pour {filename}, fallback disque")
                img = Timage(filename=filename).get_image()

            for name, roi in el.items():
                cls_ = GetDataImageRoi(data, img, roi, name,
                                       kingdom=kingdom, index=k, last_power=last_power)
                try:
                    t = threading.Thread(target=cls_.treatment, daemon=True)
                    threads.append(t)
                    t.start()
                except Exception as e:
                    logger.error(e)

        for t in threads:
            t.join()

        last_power = data.get("power")
        end_time_scan_each = time.time()  


        TODAY = datetime.today().strftime("%Y-%m-%d")
        extract_dir = os.path.join(BASE_DIR, "extract", str(kingdom), str(TODAY))
        os.makedirs(extract_dir, exist_ok=True)
        with open(os.path.join(extract_dir, f"backup_{start_created}.ndjson"), "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

        logger.info("Time: {:.2f} sec".format(end_time_scan_each - start_time_scan_each)) 
        index_range_ppl += 1
        time.sleep(0.25)
        device.shell(coords_in_game.input_gov_close)
        time.sleep(1)


    device.shell(coords_in_game.input_close_more_info)
    time.sleep(1)
    device.shell(coords_in_game.input_close_more_info)
    time.sleep(1)

    end_time_scan = time.time()  
    global_time = end_time_scan - start_time_scan
    formatted_time = time.strftime("%H:%M:%S", time.gmtime(global_time))
    logger.info("Global time: {}".format(formatted_time))
    return {"kingdom":kingdom,"time_created":start_created}






def multi_scan(multi_kd:bool,nb_scan_kd:int,*args,**kwargs)->dict:
    nb_scan = kwargs.get("players")
    start=kwargs.get("start_scan")
    power_min=kwargs.get("power_min")
    format_export = kwargs.get('format_export')
    rois=[(400,240,120,50),(1000,240,120,50)]
    coords_in_game = CoordsGamesInteraction()
    device = scan_get_devices()
    for kd in range(start,nb_scan_kd+1):
        
        """ ecrire le process de selection de kd ?"""
        """ Scan => """
        data = scan(nb_scan=nb_scan,start = start,power_min=power_min,device=device)
        export_data = ExportData(el=data)
        if format_export == "csv":
            export_data.export_to_csv()
        else:
            export_data.export_to_excel()
        """ ecrire le process de changement de kd """
        time.sleep(5)
        if nb_scan_kd == 1:
            device.shell(coords_in_game.input_gov_close)
            return True
        #logger.info("open menu")
        #device.shell(coords_in_game.open_gov)
        logger.info("Open settings")
        device.shell(coords_in_game.input_open_settings)
        time.sleep(2)
        logger.info("open characters")
        device.shell(coords_in_game.input_open_characters)
        time.sleep(4)
        logger.info("swipe header")
        device.shell(coords_in_game.swipe_top_characters)
        time.sleep(4)

        if kd == nb_scan_kd:
            roi = rois[0]
            device.shell(f"input tap {roi[0]} {roi[1]}")
            time.sleep(2)
            logger.info("return origin kd")
            device.shell(coords_in_game.input_btn_confirm_change)
            time.sleep(30)
        
        for _ in range(kd//2):
            logger.info("swipe search kd")
            device.shell(coords_in_game.swipe_account_characrers)

        if kd%2 ==0:
            roi = rois[0]
        else:
            roi = rois[1]

        time.sleep(2)
        device.shell(f"input tap {roi[0]} {roi[1]}")
        time.sleep(5)
        device.shell(coords_in_game.input_btn_confirm_change)
        time.sleep(10)
        device.shell("input tap 800 500")
        time.sleep(30)
    return True
            