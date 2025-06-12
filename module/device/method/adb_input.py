import time
from functools import wraps

from adbutils import AdbError

from module.base.decorator import del_cached_property
from module.base.utils import ensure_int, point2str
from module.device.connection import Connection
from module.device.method.utils import RETRY_TRIES, retry_sleep, handle_adb_error
from module.exception import RequestHumanTakeover
from module.logger import logger


def retry(func):
    @wraps(func)
    def retry_wrapper(self, *args, **kwargs):
        """
        Args:
            self (AdbInput):
        """
        init = None
        for _ in range(RETRY_TRIES):
            try:
                if callable(init):
                    retry_sleep(_)
                    init()
                return func(self, *args, **kwargs)
            # Can't handle
            except RequestHumanTakeover:
                break
            # When adb server was killed
            except ConnectionResetError as e:
                logger.error(e)

                def init():
                    self.adb_reconnect()
            # AdbError
            except AdbError as e:
                if handle_adb_error(e):
                    def init():
                        self.adb_reconnect()
                else:
                    break
            # Unknown
            except Exception as e:
                logger.exception(e)

                def init():
                    pass

        logger.critical(f'Retry {func.__name__}() failed')
        raise RequestHumanTakeover

    return retry_wrapper


class AdbInput(Connection):
    """ADB input commands for touch control and app management"""
    
    @retry
    def click_adb(self, x, y):
        """
        Click using adb input tap command.
        
        Args:
            x (int): x coordinate
            y (int): y coordinate
        """
        x, y = ensure_int(x, y)
        cmd = ['input', 'tap', str(x), str(y)]
        self.adb_shell(cmd)
        # Small delay to ensure click is registered
        time.sleep(0.05)
    
    @retry
    def swipe_adb(self, p1, p2, duration=200):
        """
        Swipe using adb input swipe command.
        
        Args:
            p1 (tuple): Starting point (x1, y1)
            p2 (tuple): Ending point (x2, y2)
            duration (int): Duration of swipe in milliseconds
        """
        x1, y1 = ensure_int(p1[0], p1[1])
        x2, y2 = ensure_int(p2[0], p2[1])
        cmd = ['input', 'swipe', str(x1), str(y1), str(x2), str(y2), str(duration)]
        self.adb_shell(cmd)
        # Small delay after swipe
        time.sleep(0.05)
    
    @retry
    def drag_adb(self, p1, p2, duration=1000):
        """
        Drag using adb input swipe command with longer duration.
        Similar to swipe but with longer press time for drag operations.
        
        Args:
            p1 (tuple): Starting point (x1, y1)
            p2 (tuple): Ending point (x2, y2)
            duration (int): Duration of drag in milliseconds
        """
        x1, y1 = ensure_int(p1[0], p1[1])
        x2, y2 = ensure_int(p2[0], p2[1])
        cmd = ['input', 'swipe', str(x1), str(y1), str(x2), str(y2), str(duration)]
        self.adb_shell(cmd)
        # Longer delay after drag
        time.sleep(0.5)
    
    @retry
    def app_current_adb(self):
        """
        Get current running app package name using ADB.
        
        Returns:
            str: Package name of current foreground app
        """
        # Get the current focused app
        result = self.adb_shell(['dumpsys', 'window', 'windows'], timeout=10)
        
        # Look for mCurrentFocus or mFocusedApp
        import re
        # Try to find mCurrentFocus first
        match = re.search(r'mCurrentFocus=Window{.*\s+(\S+)/\S+}', result)
        if match:
            return match.group(1)
        
        # Fallback to mFocusedApp
        match = re.search(r'mFocusedApp=.*\s+(\S+)/\S+', result)
        if match:
            return match.group(1)
        
        # Another fallback pattern
        match = re.search(r'Window{.*\s+(\S+)/\S+}', result)
        if match:
            return match.group(1)
            
        return ''
    
    @retry
    def app_start_adb(self, package_name=None):
        """
        Start app using am start command with MainActivity.
        
        Args:
            package_name (str): Package name to start
        """
        if not package_name:
            package_name = self.package
            
        # Use am start to launch the MainActivity
        cmd = ['am', 'start', '-n', f'{package_name}/com.shiftup.nk.MainActivity']
        result = self.adb_shell(cmd)
        
        # Small delay to let the app start
        time.sleep(1)
        
        # Click at (250, 615) to handle any initial screen
        logger.info('Clicking initial screen at (250, 615)')
        self.click_adb(250, 615)
        
        # Additional delay after click
        time.sleep(1)
        
        # Verify the app started
        current = self.app_current_adb()
        if current != package_name:
            logger.warning(f'Failed to start {package_name}, current app is {current}')
    
    @retry
    def app_stop_adb(self, package_name=None):
        """
        Stop app using am force-stop command.
        
        Args:
            package_name (str): Package name to stop
        """
        if not package_name:
            package_name = self.package
            
        cmd = ['am', 'force-stop', package_name]
        self.adb_shell(cmd)
        
        # Small delay after stopping
        time.sleep(0.5)