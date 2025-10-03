import pytesseract
import re 
import time 
import pyperclip
from utils.scan_manager import CoordScanOcrPlayers
from utils.mx_std_values import StandarsValueScanOcr
from utils.image_manager import GetDataImage
import logging 
logger = logging.getLogger(__name__)


class GetValueImageScan:
    """
    Partir du principe que chaque joueur est un Objet
    Chaque image d'un joueur et un sous objet de celui-c 
    """
    def __init__(self,device,name,data,image,roi,index):
        self.image = image
        self.device = device
        self.name = name
        self.roi = roi
        self.data = data
        self.index_ = index
        
    def get_governor_name(self, *args, **kwargs):
        import time, pyperclip

        governor_name_previous = kwargs.get("governor_name_previous")
        max_retries = 5
        sleep = 0.5

        governor_name = ""

        for attempt in range(max_retries):
            # clic sur la zone de copie
            self.device.shell(self.roi)
            time.sleep(sleep)

            try:
                governor_name = pyperclip.paste().strip()
            except Exception as e:
                logger.warning(f"Clipboard read failed (attempt {attempt+1}): {e}")
                governor_name = ""

            if governor_name and governor_name != governor_name_previous:
                logger.info(f"Governor name obtenu: {governor_name}")
                return governor_name

            time.sleep(sleep)

        # fallback si rien
        logger.warning("Impossible de copier le governor_name, fallback sur index")
        return str(self.index_)
 


class GetDataImageRoi:
    def __init__(self, data, image, roi, name, *,
                 kingdom=None, index=None, last_power=None, **kwargs):
        self.image = image
        self.roi = roi
        self.name = name
        self.data = data

        # options OCR / preprocessing
        self.kwargs = dict(kwargs)           
        self.kingdom = kingdom
        self.index = index
        self.last_power = last_power or 0

        # image prétraitée initiale
        try:
            self.data_image = GetDataImage(image, roi, px_img=17, **self.kwargs).process_()
        except Exception as e:
            logger.error(str(e))
            pass
    def get_governor_id_kd(self):
        values=pytesseract.image_to_string(self.data_image,config='--psm 10 --oem 1')
        data_extract =  re.findall(r"(?!\#)([\d]+)",values) 
        logger.info(data_extract)
        try:
            
            gov_id=int(data_extract[0])
            try:
                id_kingdom = int(data_extract[1])
            except:
                id_kingdom=""
        except:
            gov_id="".join(data_extract)
            id_kingdom=""

        return [gov_id,id_kingdom]
    

    def treatment(self):
        self.kwargs.update({"gray":True,"name":self.name})

        if self.name == "alliance" or self.name =="civilisation":
            values = StandarsValueScanOcr(self.data_image).get_value_string()
            

        else:
            try:
                values=StandarsValueScanOcr(self.data_image).get_value_int()
                list_px =[i for i in range(17,201,2)]
                counter = 0
                while values == 0 and self.last_power >= 40000000 and counter < 21:
                    px = list_px[counter]

                    self.data_image = GetDataImage(self.image,self.roi,px_img=px,kwargs=self.kwargs).process_()
                    values=StandarsValueScanOcr(self.data_image).get_value_int()
                    counter+=1
                    logger.info(f"{self.name} => {values} => {px} : {self.roi}")
                    if counter > 5:
                        
                        self.kwargs.update({"blur":True})
                    if counter >10:
                       self.kwargs.update({"thresh":True})
                    if values > 0:
                        break
                    if counter >20:
                        break
            except Exception as e:
                logger.error(e)
                values=0
        logger.info("{} => {}".format(self.name,values))
            
        return self.data.update({self.name:values})
        
