
import cv2
import numpy as np
import re 
from .mx_std_values import StandarsValueScanOcr
import time
import logging
logger = logging.getLogger(__name__)
class Timage:
	
    def __init__(self,image=None,filename=None,roi=None,*args,**kwargs):
        self.image = image
        self.filename = filename
        self.pathfile = f"img/{self.filename}.png"
        self.args = args
        self.kwargs = kwargs
        self.roi = roi

    def create_image(self):
        with open(('img/{}.png'.format(self.filename)), 'wb') as f:
            f.write(self.image)

    

    def crop_image(self):
        # Lire l'image créée
        x, y, width, height = self.roi
        image = cv2.imread(f'img/{self.filename}.png')
        
        # Recadrer l'image
        cropped_image = image[y:y+height, x:x+width]
        # Enregistrer l'image recadrée
        cv2.imwrite(f'img/crop_{self.filename}.png', cropped_image)


    def get_image(self):
        img = cv2.imread(self.pathfile)
        kernel = np.ones((2,2),np.uint8)
        image = cv2.dilate(img,kernel)
        inversed = self.kwargs.get("inversed")
        if inversed == True:
            image = cv2.bitwise_not(img)
        return image
		

class GetDataImage:
    def __init__(self,image,roi,px_img,*args,**kwargs):
        self.image = image
        self.roi = roi
        self.args = args
        self.kwargs = kwargs
        self.px_img = px_img

    def get_roi_image(self):
        roi = self.roi
        return self.image[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]
        
    
    def get_treatment_image(self):
        image = self.get_roi_image()
        image_recadree_grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        alpha, beta = 1.3, 10
        image_recadree_grayscale = cv2.convertScaleAbs(image_recadree_grayscale, alpha=alpha, beta=beta)
        
        edges = self.kwargs.get("edges")
        gray = self.kwargs.get("gray")
        name = self.kwargs.get("name")
        if self.kwargs.get("blur"):
            image_recadree_grayscale = cv2.GaussianBlur(image_recadree_grayscale, (3, 3), 0)
        if self.kwargs.get('thresh'):
            thresh = cv2.adaptiveThreshold(image_recadree_grayscale, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, self.px_img, -4)
            cv2.imwrite(f"img/thresh_{name}.png",thresh)
        else:
            cv2.imwrite(f"img/gray_{name}.png",image_recadree_grayscale)
        return image_recadree_grayscale

    
    def process_(self):
        return  self.get_treatment_image()
		


 
class TreatmentScreenshotControlManager:
    def __init__(self,device,filename:str,coord:list,roi:tuple):
        """
        Crée l'image
        Applique un traitement à l'image
        Contrôle que les screenshots comprends les informations demandées
        """
        self.device = device
        self.filename = filename
        self.coord = coord
        self.roi = roi 
        self.px_img = 31 

    def screenshot_get_data(self,*args,**kwargs):
        """ Prend les screenshot 
        Contrôle que les images soient celles demandées
        """
        name_ =False

        logger.info(f"open coord,{self.filename}")
        path_file = "img/{}.png".format(self.filename)

        
        k = kwargs.get("index_k")
        kwargs = {"inversed":False}
        kwargs.update({"gray":True})
        count=0
        while not name_:
            open_coord = self.coord[0]
            print(count,open_coord)
            
            self.device.shell(open_coord)
            time.sleep(0.50)
            if self.filename == "gov_info":
                self.device.shell('input tap 1180 200') # si rally ou pop up 
                time.sleep(0.30)
            image = self.device.screencap()
            time.sleep(0.50)
            Timg = Timage(image,self.filename)
            Timg.create_image()
            logger.info(f"Screenshot of {self.filename}")

            image =Timg.get_image()

            logger.info(f"get image {self.filename} for control")
            data_image = GetDataImage(image,self.roi,px_img=31,**kwargs).process_()
            values=StandarsValueScanOcr(data_image).get_value_string()
            roi_gov=(595,190,110,40)
            if self.filename =="gov_info":
                kwargs ={"inversed":True,"gray":True}
                self.px_img = 101
                data_governor = data_image
                value_gov = StandarsValueScanOcr(data_governor).get_value_string().lstrip().lower().replace(" ","")
                logger.info("value governor ? = {}".format(value_gov))
            values =values.lstrip().lower().replace(" ","_").replace("-","")
            logger.info(values)
            
            if  not re.search("governor_profile",values)  and self.filename == "gov_info" and not re.search("governor",value_gov):
    
                    logger.warning("values not conform")            
                    time.sleep(0.30)
                    self.device.shell(f'input tap 280 ' + str(k))
                    count += 1
                    if count == 3:
                        self.device.shell(f'input tap 280 ' + str(k+100))
            else:
                if  (re.search("(governor_profile|more_info|kill_statistics)",values)):
                    logger.info(f"value done {self.filename} {values}")
                    
                    name_ = True
                
                else:
                    count+=1
            if count>4:
                break


        if len(self.coord) == 2:
            close_coord = self.coord[1]
            time.sleep(0.50)
            self.device.shell(close_coord)