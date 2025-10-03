
import cv2
import numpy as np
import re 
from .mx_std_values import StandarsValueScanOcr
import time
import logging
import re
from utils.mx_std_values import StandarsValueScanOcr
logger = logging.getLogger(__name__)
import io
from PIL import Image
import os

import cv2, numpy as np, os


class Timage:
    def __init__(self, image=None, filename=None, roi=None, pathfile=None, *args, **kwargs):
        self.image = image
        self.filename = filename
        self.roi = roi
        self.kwargs = kwargs
        self.pathfile = pathfile or f"img/{self.filename}.png"
        self._cv_img = None  # cache RAM

    def create_image(self):
        """Compatibilité: écrit le screenshot sur disque ET met en cache RAM."""
        if self.image is None:
            return
        os.makedirs("img", exist_ok=True)
        with open(self.pathfile, "wb") as f:
            f.write(self.image)

        # cache RAM fidèle à imread()
        if isinstance(self.image, (bytes, bytearray)):
            arr = np.frombuffer(self.image, np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)  # même rendu que imread()
            if img is None:
                raise ValueError("Timage.create_image: imdecode a échoué")
            self._cv_img = img
        elif isinstance(self.image, np.ndarray):
            if len(self.image.shape) == 3 and self.image.shape[2] == 3:
                self._cv_img = self.image.copy()
            elif len(self.image.shape) == 2:
                self._cv_img = cv2.cvtColor(self.image, cv2.COLOR_GRAY2BGR)
            else:
                raise ValueError("Timage.create_image: ndarray au format inattendu")

    def crop_image(self):
        x, y, width, height = self.roi
        img = self.get_image()
        cropped_image = img[y:y+height, x:x+width]
        cv2.imwrite(f"img/crop_{self.filename}.png", cropped_image)

    def get_image(self):
        """
        Retourne l'image BGR strictement équivalente à cv2.imread() depuis les bytes.
        ⚠️ Aucun resize/filtre ici, pour ne pas décaler tes ROI.
        """
        if self._cv_img is not None:
            img = self._cv_img
        elif isinstance(self.image, (bytes, bytearray)):
            arr = np.frombuffer(self.image, np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)  # même rendu qu'imread()
            if img is None:
                raise ValueError("Timage.get_image: imdecode a échoué")
            self._cv_img = img
        elif isinstance(self.image, np.ndarray):
            if len(self.image.shape) == 3 and self.image.shape[2] == 3:
                img = self.image.copy()
            elif len(self.image.shape) == 2:
                img = cv2.cvtColor(self.image, cv2.COLOR_GRAY2BGR)
            else:
                raise ValueError("Timage.get_image: ndarray au format inattendu")
            self._cv_img = img
        else:
            img = cv2.imread(self.pathfile, cv2.IMREAD_COLOR)  # fallback compat
            if img is None:
                raise FileNotFoundError(f"Impossible de charger {self.pathfile}")
            self._cv_img = img

        if self.kwargs.get("inversed"):
            img = cv2.bitwise_not(img)
        return img



class GetDataImage:
    def __init__(self, image, roi, px_img, *args, **kwargs):
        """
        image : numpy array (BGR) venant de Timage.get_image()
        roi   : (x,y,w,h)
        px_img: taille utilisée pour adaptiveThreshold
        """
        self.image = image
        self.roi = roi
        self.args = args
        self.kwargs = kwargs
        self.px_img = px_img

    def get_roi_image(self):
        x, y, w, h = map(int, self.roi)
        H, W = self.image.shape[:2]

        # clamp dans l'image
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(W, x + w)
        y1 = min(H, y + h)

        if x0 >= x1 or y0 >= y1:
            # on log clairement l'info pour debug, plutôt que de planter plus loin
            raise ValueError(f"ROI hors image: roi={self.roi}, image={W}x{H}")

        return self.image[y0:y1, x0:x1]
    def get_treatment_image(self):
        roi_img = self.get_roi_image()

        # conversion en niveau de gris
        gray_img = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)

        # amélioration du contraste
        alpha, beta = 1.3, 10
        gray_img = cv2.convertScaleAbs(gray_img, alpha=alpha, beta=beta)

        # options
        if self.kwargs.get("blur"):
            gray_img = cv2.GaussianBlur(gray_img, (3, 3), 0)

        name = self.kwargs.get("name", "unknown")
        save_debug = self.kwargs.get("save_debug", True)  # <--- NEW

        if self.kwargs.get("thresh"):
            proc = cv2.adaptiveThreshold(
                gray_img, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                self.px_img, -4
            )
            kernel = np.ones((2, 2), np.uint8)
            proc = cv2.morphologyEx(proc, cv2.MORPH_OPEN, kernel)
            if save_debug:
                os.makedirs("img", exist_ok=True)
                cv2.imwrite(f"img/thresh_{name}.png", proc)
        else:
            proc = gray_img
            if save_debug:
                os.makedirs("img", exist_ok=True)
                cv2.imwrite(f"img/gray_{name}.png", proc)

        return proc

    def process_(self):
        return self.get_treatment_image()



 
def normalize_header(val: str) -> str:
    """Corrige les erreurs OCR fréquentes sur les titres de page."""
    val = val.lower().replace(" ", "_").replace("-", "")
    if "governor" in val or "profile" in val:
        return "governor_profile"
    if "kill" in val:
        return "kill_statistics"
    if "info" in val:
        return "more_info"
    return val


class TreatmentScreenshotControlManager:
    def __init__(self, device, filename: str, coord: list, roi: tuple, save_debug: bool = True):
        self.device = device
        self.filename = filename
        self.coord = coord
        self.roi = roi
        self.px_img = 31
        self.save_debug = save_debug
        self.last_image = None  # stockage temporaire

    def screenshot_get_data(self, *args, **kwargs):
        """Capture et validation OCR de la page, renvoie toujours une nouvelle image."""
        self.last_image = None  # ⚡ reset à chaque appel

        name_ok = False
        logger.info(f"open coord,{self.filename}")

        k = kwargs.get("index_k")
        kwargs_ocr = {"inversed": False, "gray": True}

        count = 0
        value_gov = ""

        while not name_ok:
            open_coord = self.coord[0]
            logger.info(f"{count} {open_coord}")
            self.device.shell(open_coord)
            time.sleep(0.5)

            if self.filename == "gov_info":
                self.device.shell("input tap 1180 200")  # ferme popup rally
                time.sleep(0.3)

            # --- capture RAM ---
            image_bytes = self.device.screencap()
            img = Timage(image=image_bytes, filename=self.filename).get_image()

            if self.save_debug:
                cv2.imwrite(f"img/{self.filename}.png", img)

            logger.info(f"Screenshot of {self.filename} (RAM mode)")

            # --- OCR header robuste ---
            try:
                data_image = GetDataImage(img, self.roi, px_img=self.px_img, **kwargs_ocr).process_()
                if data_image is None:
                    raise ValueError("process_() returned None")

                values = StandarsValueScanOcr(data_image).get_value_string()
                values_norm = normalize_header(values)

            except Exception as e:
                logger.error(f"[{self.filename}] OCR header failed on ROI {self.roi}: {e}")
                # ⚡ si OCR échoue → reprendre un screenshot immédiatement
                image_bytes = self.device.screencap()
                img = Timage(image=image_bytes, filename=f"{self.filename}_retry").get_image()
                data_image = GetDataImage(img, self.roi, px_img=self.px_img, **kwargs_ocr).process_()
                values = StandarsValueScanOcr(data_image).get_value_string()
                values_norm = normalize_header(values)

            if self.filename == "gov_info":
                value_gov = (
                    StandarsValueScanOcr(data_image)
                    .get_value_string()
                    .strip()
                    .lower()
                    .replace(" ", "")
                )
                logger.info(f"value governor ? = {value_gov}")

            logger.info(f"OCR header={values_norm}")

            # --- validation ---
            if (
                self.filename == "gov_info"
                and values_norm != "governor_profile"
                and "governor" not in value_gov
            ):
                logger.warning("values not conform → tap 1163 80 + retry OCR")
                time.sleep(0.3)

                # ⚡ nouveau : tap sur (1163, 80)
                self.device.shell("input tap 1163 80")
                time.sleep(0.5)

                # ⚡ reprendre un screen après le tap
                image_bytes = self.device.screencap()
                img = Timage(image=image_bytes, filename=f"{self.filename}_retry2").get_image()
                data_image = GetDataImage(img, self.roi, px_img=self.px_img, **kwargs_ocr).process_()
                values = StandarsValueScanOcr(data_image).get_value_string()
                values_norm = normalize_header(values)

                # on refait un check direct
                if values_norm in ("governor_profile", "more_info", "kill_statistics") or "governor" in values.lower():
                    logger.info(f"[retry] value done {self.filename} {values_norm}")
                    self.last_image = img
                    name_ok = True
                    continue

                # si toujours pas → fallback ancien flow
                self.device.shell(f"input tap 280 {k}")
                count += 1
                if count == 3:
                    self.device.shell(f"input tap 280 {k+100}")

            else:
                if values_norm in ("governor_profile", "more_info", "kill_statistics"):
                    logger.info(f"value done {self.filename} {values_norm}")
                    self.last_image = img  # ⚡ toujours mis à jour
                    name_ok = True
                else:
                    count += 1

            if count > 4:
                break

        if len(self.coord) == 2:
            close_coord = self.coord[1]
            time.sleep(0.5)
            self.device.shell(close_coord)

        return self.last_image  # ⚡ nouvelle image validée



class TreatmentVideoControlManager:
    """
    Trouve dans une vidéo la frame où l'en-tête attendu apparaît (regex sur ROI de contrôle),
    et écrit img/{filename}.png pour rester 100% compatible avec le pipeline existant.
    """
    def __init__(self, cap, filename: str, ctrl_roi: tuple, save_path: str = None):
        """
        cap: cv2.VideoCapture ouvert sur la vidéo du joueur
        filename: 'gov_info' | 'kills_tier' | 'more_info'
        ctrl_roi: (x,y,w,h) pour l'en-tête à reconnaître
        save_path: chemin final pour l'image (par défaut img/{filename}.png)
        """
        self.cap = cap
        self.filename = filename
        self.ctrl_roi = ctrl_roi
        self.save_path = save_path or f"img/{filename}.png"
        self.px_img = 31

    def _roi_text_ok(self, frame_bgr, expect_regex: str) -> bool:
        x, y, w, h = self.ctrl_roi
        crop = frame_bgr[y:y+h, x:x+w]
        proc = GetDataImage(crop, (0,0,w,h), px_img=self.px_img, gray=True, name=self.filename).process_()
        txt = StandarsValueScanOcr(proc).get_value_string()
        norm = txt.strip().lower().replace(" ","_").replace("-","")
        return re.search(expect_regex, norm) is not None

    def extract_and_save(self, expect_regex: str, search_start: int, search_len: int, stride: int = 1) -> int:
        """
        Cherche dans [search_start, search_start+search_len) la frame qui matche expect_regex.
        Sauve l'image au chemin attendu. Retourne l'index de frame retenu, sinon -1 (avec fallback).
        """
        total = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        i0 = max(0, min(total-1, search_start))
        i1 = max(0, min(total, search_start + max(1, search_len)))

        chosen = -1
        for idx in range(i0, i1, max(1, stride)):
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = self.cap.read()
            if not ret or frame is None:
                break
            if self._roi_text_ok(frame, expect_regex):
                cv2.imwrite(self.save_path, frame)
                chosen = idx
                break

        if chosen == -1:
            # fallback : frame milieu de la zone
            mid = (i0 + i1) // 2
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, mid)
            ret, frame = self.cap.read()
            if ret and frame is not None:
                cv2.imwrite(self.save_path, frame)
                chosen = mid

        return chosen
