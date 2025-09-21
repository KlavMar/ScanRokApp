
from ppadb.client import Client
import os
import time
from services.connect import BluestackConnect
from services.timage import Timage,GetDataImage
import pytesseract
import re
import sys
import logging
import tkinter as tk
from services.scan_ocr import get_scan
os.environ["TESSERACT_LOG"] = "ERROR"
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' 
logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")

def get_devices():
    adb = Client(host='localhost', port=5037)

    devices = adb.devices()

    
    return devices
def get_value_string(image):
    value=pytesseract.image_to_string(image,config='--psm 10 --oem 3')
    return value

def get_value_int(image):

	value=pytesseract.image_to_string(image,config='--psm 10 --oem 3')
	try:
		return int("".join(re.findall(r"[\d]{4}",value)))
	except:
		return 0

conn = BluestackConnect()

if len(sys.argv)<2:
    conn.get_open()
    time.sleep(90)
for port in range(5555,5600):
    try:
        conn.get_connect(port=port)
        devices = get_devices()
        if devices:
             logging.info(devices)
             break
    except Exception as e:
        logging.error(e)


#Prolly a good idea to have only 1 device while running this
device = devices[0]

kwargs = {"inversed":False}
kwargs.update({"gray":True})

open_gov = 'input tap 70 54'
rois=[(400,240,120,50)]
rois.append((1000,240,120,50))


nb_kingdom =16
try:
    nb_start = int(sys.argv[1])
except:
     nb_start =1
logging.info(nb_start)
for i in range(nb_start,nb_kingdom+1):
   # device.shell("input tap 807  645") # click Wall fail
    #logging.info("tap wall fail ?")
    roi = (740,155,100,50)
    image = device.screencap()
    screenshot_name = f"info_wall_fall"
    screenshot_path = path_file = "img/{}.png".format(screenshot_name)
    Timage(image,screenshot_name).create_image()
    img =Timage(filename=screenshot_name,pathfile=screenshot_path,**kwargs)
    image = img.get_image()
    #kwargs.update({"name":i})
    data_image = GetDataImage(image,roi,px_img=181,**kwargs).process_()
    value =get_value_string(data_image).lower()
    logging.info(value)

    if value == "info" : 
        device.shell("input tap 807  645") # click Wall fail
        logging.info("tap wall fail ?")
        time.sleep(5)

        time.sleep(2)
        #device.shell("input tap 78 834")

          
    else:
        time.sleep(5)
        device.shell("input tap 78 834") # dezoom sur map
    time.sleep(2)
    device.shell("input tap 377 33") # barre de recherche
    logging.info("search bar")
    time.sleep(1.5)
    device.shell("input tap 536 175") # open input kindom text
    logging.info("kingdom text")
    time.sleep(1)
    kingdom  = ""
    root = tk.Tk()      
    root.withdraw()
    max_tries = 10
    tries = 0

    while tries<max_tries:
        device.shell("input tap 53 823")
        device.shell("input tap 53 823")
        time.sleep(1)
        device.shell("input keyevent KEYCODE_COPY")

        clipboard_content = root.clipboard_get()
  
        try:
            kingdom = int(clipboard_content)
            logging.info(f"kingdom = {kingdom}")
            break
        except ValueError:
            logging.error(f"Kingdom not int {clipboard_content}")
            tries+=1
            time.sleep(1) 
        finally:
            device.shell("input keyevent KEYCODE_ENTER")
            device.shell("input tap 377 33") 

    logging.info(kingdom)
    time.sleep(3)
     #### scan start ###
    get_scan(kingdom,250,1,kvk=True)
    ### scan end ####
    time.sleep(5)
    
    device.shell(open_gov)
    logging.info("open gov)")
    time.sleep(1)
    device.shell("input tap 1380 740") # open settings
    logging.info("open settings")
    time.sleep(1)
    device.shell("input tap 436 465") #open characters 
    logging.info("open characters")
    time.sleep(5)

    device.shell("input swipe 800 340 800 269 1500")
    
    logging.info("swipe first")

    time.sleep(2)
    if i == nb_kingdom:
        roi = rois[0]
        device.shell(f"input tap {roi[0]} {roi[1]}")
        time.sleep(2)
        device.shell("input tap 1026 640")
        time.sleep(30)
          
    for _ in range(i//2):
            device.shell("input swipe 800 340 800 200 1500")
            logging.info(f"{i} swipe search kingdom")
            time.sleep(3)
    
   # image = device.screencap()

    #Timage(image,screenshot_name).create_image()
    if i%2 ==0:
        roi = rois[0]
    else:
        roi = rois[1]
    logging.info(roi)
    """
    img =Timage(filename=screenshot_name,pathfile=screenshot_path,**kwargs)
    image = img.get_image()
    #kwargs.update({"name":i})
    data_image = GetDataImage(image,roi,px_img=181,**kwargs).process_()
    kingdom=get_value_int(data_image)
    logging.info("Kingdom {}".format(kingdom))
    """
    #### procédure de clic pour changer de kingdom ####
    time.sleep(2)
    device.shell(f"input tap {roi[0]} {roi[1]}")
    time.sleep(5)
    device.shell("input tap 1026 640")
    time.sleep(20)

    

    

        