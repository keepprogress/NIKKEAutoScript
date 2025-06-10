import cv2
import numpy as np
from functools import wraps

from module.device.connection import Connection, retry
from module.device.method.utils import ImageTruncated
from module.exception import RequestHumanTakeover
from module.logger import logger


class Adb(Connection):
    @retry
    def screenshot_adb(self):
        """
        Take a screenshot using adb screencap command.
        
        Returns:
            np.ndarray: Screenshot in RGB format (720x1280x3)
        """
        # Execute screencap command and get PNG data
        # Using exec-out to get binary output directly without creating a file on device
        image_data = self.adb_shell(['screencap', '-p'], stream=True, recvall=True)
        
        if not image_data:
            raise ImageTruncated('Empty image data from adb screencap')
        
        # Convert PNG bytes to numpy array
        image_array = np.frombuffer(image_data, np.uint8)
        if image_array.size == 0:
            raise ImageTruncated('Empty image array after reading from buffer')
        
        # Decode PNG to get BGR image
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if image is None:
            raise ImageTruncated('Failed to decode PNG image')
        
        # Convert BGR to RGB (cv2 uses BGR by default)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        if image is None:
            raise ImageTruncated('Failed to convert BGR to RGB')
        
        # The image from screencap is in RGBA format, but after cv2.imdecode with IMREAD_COLOR,
        # it's already converted to RGB (3 channels), discarding the alpha channel
        
        return image
