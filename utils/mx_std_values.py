
import pytesseract
import re 
class StandarsValueScanOcr:
    def __init__(self,image):
        self.image  = image

    def get_value_int(self):

        value=pytesseract.image_to_string(self.image,config='--psm 7 --oem 1 -c tessedit_char_whitelist=0123456789')
        try:
            return int("".join(re.findall(r"[\d]*",value)))
        except:
            return 0

    def get_value_string(self):
        value=pytesseract.image_to_string(self.image,config='--psm 10 --oem 1')
        value = value.lstrip().rstrip()
        return value
