

from ppadb.client import Client
import subprocess
import os,sys
import logging
from settings import BASE_DIR
logger = logging.getLogger(__name__)


class BluestackDeviceManager:
    def __init__(self,port):
        self.port = port 
        self.android_dir = os.path.join(BASE_DIR,"android")
        self.initial_dir = BASE_DIR


    def get_connect(self,port=5555):
        
        try:
            os.chdir(self.android_dir)
            subprocess.run(['adb', 'kill-server'], check=True)
            subprocess.run(['adb', 'connect', f'localhost:{port}'], check=True)
            return (f"Executed 'adb connect localhost:{port}]'")

        except subprocess.CalledProcessError as e:
            return (f"An error occurred while executing the command: {e}")
        except Exception as e:
            return (f"An unexpected error occurred: {e}")
        finally:
            os.chdir(self.initial_dir)  
            

    def get_devices(self):
       
        try:
            adb = Client(host='localhost', port=self.port)
        except Exception as e:
            logger.error(e)
        devices = adb.devices()

        if len(devices) == 0:
             #logger.error('no device attached')
            logger.warning('no deviced')
        return devices