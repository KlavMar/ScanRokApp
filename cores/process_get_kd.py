   # self.device.shell("input tap 807  645") # click Wall fail
    #logging.info("tap wall fail ?")
from utils.image_manager import GetDataImage,Timage
from utils.mx_std_values import StandarsValueScanOcr
from utils.bluestack_manager import BluestackDeviceManager
import logging
import time
import pyperclip
logger = logging.getLogger(__name__)

class ProcessGetKd:
    def __init__(self,device):
        self.device = device
    

    def get_kingdom_by_image(self,**kwargs):

        roi = (740,155,100,50)
        image = self.device.screencap()
        screenshot_name = f"info_wall_fall"
        screenshot_path  = "img/{}.png".format(screenshot_name)
        Timage(image,screenshot_name).create_image()
        img =Timage(filename=screenshot_name,pathfile=screenshot_path,**kwargs)
        image = img.get_image()
        #kwargs.update({"name":i})
        data_image = GetDataImage(image,roi,px_img=181,**kwargs).process_()
        value =StandarsValueScanOcr(data_image).get_value_string()
        value = value.lower()
        logging.info(value)

        if value == "info" : 
            self.device.shell("input tap 807  645") # click Wall fail
            logging.info("tap wall fail ?")
            time.sleep(5)

            time.sleep(2)
            #self.device.shell("input tap 78 834")

            
        else:
            time.sleep(5)
            self.device.shell("input tap 78 834") # dezoom sur map
        time.sleep(2)
        self.device.shell("input tap 377 33") # barre de recherche
        logging.info("search bar")
        time.sleep(1.5)
        self.device.shell("input tap 536 175") # open input kindom text
        logging.info("kingdom text")
        time.sleep(1)
        kingdom  = ""
        max_tries = 10
        tries = 0

        while tries<max_tries:
            self.device.shell("input tap 53 823")
            self.device.shell("input tap 53 823")
            time.sleep(1)
            self.device.shell("input keyevent KEYCODE_COPY")

            clipboard_content = pyperclip.paste()

            try:
                kingdom = int(clipboard_content)
                logging.info(f"kingdom = {kingdom}")
                break
            except ValueError:
                logging.error(f"Kingdom not int {clipboard_content}")
                tries+=1
                time.sleep(1) 
            finally:
                self.device.shell("input keyevent KEYCODE_ENTER")
                time.sleep(1.00)
                
        return kingdom
