
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
logger = logging.getLogger(__name__)
def scan(nb_scan:int=None,start:int=None,power_min:int=None)->dict:
    Y=285
    start_time_scan= time.time() 

    min_power = power_min if power_min else 1000000
    
    nb_scan = nb_scan if nb_scan else 1000
    coords_in_game = CoordsGamesInteraction()


    data_scan = dict() # dictionnaire governor
    manager = BluestackDeviceManager(port=5037)  
    logger.info(manager.get_connect(port=5555))
    devices = manager.get_devices()
    if not devices:
        logger.info("Aucun device détecté")
        exit()

    device = devices[0]
    logger.info("Device connecté :%s" ,device)

    kwargs = {"inversed":False}
    kwargs.update({"gray":True})
    ### copier toutes les images liés à chaque gouvernor 
    kingdom = ProcessGetKd(device=device).get_kingdom_by_image(**kwargs)
    device.shell("input tap 377 33") 
    time.sleep(5.00)
    pyperclip.copy("")
    time.sleep(1.00)
    device.shell(coords_in_game.open_gov)
    logging.info("open gov")
    time.sleep(1.00)
    device.shell(coords_in_game.open_ranking_menu)
    logging.info("open ranking")
    time.sleep(1.00)
    device.shell(coords_in_game.open_ranking_power)
    logging.info("open ranking power")
    time.sleep(1.00)
    last_power = 10*10**10 
    governor_name_previous = ""
    #for index_range_ppl in range(start-1,nb_scan+1):
    index_range_ppl=0

    while min_power < last_power:
        if index_range_ppl>nb_scan:
            break
        logger.info(f"min:{min_power} last:{last_power}")
        logger.info(index_range_ppl+1)
        start_time_scan_each = time.time()
        k = 585 if index_range_ppl >= 4 or start >=4 else Y + (index_range_ppl * 100)
        input_open_gov = f'input tap 280 ' + str(k)
        data = dict() 
        threads  = list()
        ### test open
        object_gov = CoordScanOcrPlayers()
        filenames = {"gov_info":object_gov.get_gov_info(),
                "kills_tier":object_gov.get_tiers_kill(),
                "more_info":object_gov.get_more_info()}
        for filename in filenames.keys():
            
            if filename == "gov_info" :
                coords =[input_open_gov]
            elif filename == "kills_tier":
                coords =[coords_in_game.input_open_kill_tiers]
            elif filename == "more_info":
                coords = [coords_in_game.input_open_more_info,coords_in_game.input_close_more_info]

            dict_value_img = {"gov_info":(600, 84, 450, 40),"more_info":(690,37,250,40),"kills_tier":(1070,330,200,40)}
            kwargs = {"index_k":k}

            ## Crée et récupère les images pour les contrôler
            control_image = TreatmentScreenshotControlManager(
                device=device,
                filename=filename,
                coord=coords,
                roi=dict_value_img.get(filename)
            )
            control_image.screenshot_get_data(**kwargs)

            image = Timage(filename=filename).get_image()

            if filename == "gov_info":
                roi_gov_id = object_gov.get_governor_id()
                treatment_gov  = GetDataImageRoi(
                    device=device,
                    image=image,
                    name=filename,
                    data=data,
                    roi =roi_gov_id,
                    index=0,
                    kwargs=kwargs
                    )
                governor_id,id_kingdom = treatment_gov.get_governor_id_kd()

                roi_gov_name = object_gov.get_governor_name()
                governor_name = GetValueImageScan(
                    device=device,
                    image=image,
                    name=filename,
                    data=data,
                    roi =roi_gov_name,
                    index=0
                    ).get_governor_name()

                
                data.update({"governor_id":governor_id,"id_kingdom":id_kingdom if id_kingdom else kingdom,"governor_name":governor_name})
                governor_name_previous = governor_name
                kwargs.update({"governor_name_previous":governor_name_previous})

            

        for filename,el in filenames.items():
            path_file = "img/{}.png".format(filename)
            kwargs = {"inversed":True}
            image = Timage(filename=filename,pathfile=path_file,**kwargs).get_image()
            for name,em in el.items():
                cls_ =GetDataImageRoi(data, image, em, name,
                      kingdom=kingdom, index=k, last_power=last_power)

                try:
                    t =threading.Thread(target=cls_.treatment, daemon=True)

                    threads.append(t)
                    t.start()
                except Exception as e:
                    logging.error(e)
        for t in threads:
            t.join()
        last_power = data.get("power")
        end_time_scan_each = time.time()  
        device.shell(coords_in_game.input_gov_close)
        time.sleep(1.0)
        data_scan.update({governor_id:data})
        logger.info("TIme: {:.2f} secondes".format(end_time_scan_each - start_time_scan_each)) 
        index_range_ppl+=1

    device.shell(coords_in_game.input_close_more_info)
    time.sleep(1)
    device.shell(coords_in_game.input_close_more_info)
    time.sleep(1)
    device.shell(coords_in_game.input_gov_close)
    end_time_scan= time.time()  
    global_time = end_time_scan - start_time_scan
    formatted_time = time.strftime("%H:%M:%S", time.gmtime(global_time))
    logging.info("Global time: {}".format(formatted_time))
    return data_scan


