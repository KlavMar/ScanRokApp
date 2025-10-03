# utils/video_capture.py
import os
import cv2
import time
import numpy as np
import threading
import logging

logger = logging.getLogger(__name__)

def _screencap_to_array(device):
    raw = device.screencap()  # bytes (PNG)
    arr = np.frombuffer(raw, np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)  # BGR
    return frame

class PerPlayerRecorder:
    """
    Enregistre une petite 'vidéo' locale (mp4) en capturant en continu device.screencap()
    pendant que tu fais tes clics. 1 vidéo / joueur. Suppression après traitement.
    """
    def __init__(self, device, out_dir="tmp_videos", fps=5, resolution=(1600, 900)):
        self.device = device
        self.out_dir = out_dir
        self.fps = fps
        self.resolution = resolution
        os.makedirs(self.out_dir, exist_ok=True)
        self.out_file = None

        self._running = False
        self._writer = None
        self._thread = None
        self.frames_written = 0

    def start(self, basename="player"):
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        # chemin unique
        i = 0
        while True:
            candidate = os.path.join(self.out_dir, f"{basename}{'' if i==0 else f'_{i}'}.mp4")
            if not os.path.exists(candidate):
                self.out_file = candidate
                break
            i += 1

        self._writer = cv2.VideoWriter(self.out_file, fourcc, self.fps, self.resolution)
        self._running = True
        self.frames_written = 0

        def _loop():
            period = 1.0 / max(1, self.fps)
            next_t = time.time()
            while self._running:
                try:
                    frame = _screencap_to_array(self.device)
                    if frame is None:
                        continue
                    if (frame.shape[1], frame.shape[0]) != self.resolution:
                        frame = cv2.resize(frame, self.resolution, interpolation=cv2.INTER_LINEAR)
                    self._writer.write(frame)
                    self.frames_written += 1
                except Exception as e:
                    logger.warning("record frame failed: %s", e)
                # pacing
                next_t += period
                sleep_left = next_t - time.time()
                if sleep_left > 0:
                    time.sleep(sleep_left)
                else:
                    next_t = time.time()
        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()
        logger.info("[REC] start %s", self.out_file)

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        if self._writer:
            self._writer.release()
        logger.info("[REC] stop %s (frames=%d)", self.out_file, self.frames_written)

    def open_capture(self):
        if not self.out_file or not os.path.exists(self.out_file):
            raise RuntimeError("no recorded file")
        return cv2.VideoCapture(self.out_file)

    def cleanup(self):
        if self.out_file and os.path.exists(self.out_file):
            try:
                os.remove(self.out_file)
                logger.info("[REC] deleted %s", self.out_file)
            except Exception as e:
                logger.warning("delete failed %s: %s", self.out_file, e)
