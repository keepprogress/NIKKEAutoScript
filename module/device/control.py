from functools import cached_property

import numpy as np

from module.base.button import Button
from module.base.utils import ensure_int, point2str
from module.device.method.minitouch import Minitouch
from module.device.method.adb_input import AdbInput
from module.logger import logger


class ControlMultiInheritance(Minitouch, AdbInput):
    """Multiple inheritance to get all control methods"""
    pass


class Control(ControlMultiInheritance):
    def handle_control_check(self, button):
        # Will be overridden in Device
        pass
    
    def click_coordinate(self, x, y=None):
        """Click at specific coordinates using the configured control method.
        
        This method automatically routes to the correct control method based on configuration.
        
        Args:
            x: Either x coordinate (int) or a tuple/list of (x, y) coordinates
            y: y coordinate (int) or None if x contains both coordinates
        """
        # Handle different argument patterns
        if y is None:
            # Called with single argument - could be tuple/list of coordinates
            if isinstance(x, (tuple, list)) and len(x) >= 2:
                x, y = x[0], x[1]
            else:
                raise ValueError(f"Invalid coordinates: {x}")
        
        # Ensure coordinates are integers
        x, y = ensure_int(x, y)
        
        # Route to the correct method based on control method
        method = self.config.Emulator_ControlMethod
        if method == 'minitouch':
            # Use the original minitouch implementation
            from module.device.method import minitouch
            return minitouch.Minitouch.click_minitouch(self, x, y)
        elif method == 'ADB':
            # Use ADB click
            return self.click_adb(x, y)
        else:
            # Fallback - create a button and use generic click
            from module.base.button import Button
            coord_button = Button(
                area=(x-1, y-1, x+1, y+1),
                color=(0, 0, 0),
                button=(x-1, y-1, x+1, y+1)
            )
            return self.click(coord_button, control_check=False)
    
    def swipe_coordinate(self, p1, p2):
        """Swipe between coordinates using the configured control method.
        
        Routes to the correct swipe method based on control configuration.
        """
        method = self.config.Emulator_ControlMethod
        if method == 'minitouch':
            # Use the original minitouch implementation
            from module.device.method import minitouch
            return minitouch.Minitouch.swipe_minitouch(self, p1, p2)
        elif method == 'ADB':
            # Use ADB swipe
            return self.swipe_adb(p1, p2)
        else:
            # Fallback to generic swipe
            return self.swipe(p1, p2)
    
    # Backwards compatibility aliases
    def click_minitouch(self, x, y=None):
        """Legacy alias for click_coordinate. Use click_coordinate instead."""
        return self.click_coordinate(x, y)
    
    def swipe_minitouch(self, p1, p2):
        """Legacy alias for swipe_coordinate. Use swipe_coordinate instead."""
        return self.swipe_coordinate(p1, p2)

    @cached_property
    def click_methods(self):
        return {
            'minitouch': self.click_minitouch,
            'ADB': self.click_adb,
        }

    def click(self, button: Button, control_check=True):
        """Method to click a button.

        Args:
            button (button.Button): AzurLane Button instance.
            control_check (bool):
        """
        if control_check:
            self.handle_control_check(button)

        # x, y = random_rectangle_point(button.button)
        x, y = button.location

        x, y = ensure_int(x, y)
        logger.info(
            'Click %s @ %s' % (point2str(x, y), button)
        )
        method = self.click_methods.get(
            self.config.Emulator_ControlMethod)
        method(x, y)

    def swipe(self, p1, p2, name='SWIPE', label='Swipe', distance_check=True, handle_control_check=True):
        if handle_control_check:
            self.handle_control_check(name)
        p1, p2 = ensure_int(p1, p2)
        method = self.config.Emulator_ControlMethod
        logger.info('%s %s -> %s' % (label, point2str(*p1), point2str(*p2)))

        if distance_check:
            if np.linalg.norm(np.subtract(p1, p2)) < 10:
                # Should swipe a certain distance, otherwise AL will treat it as click.
                # uiautomator2 should >= 6px, minitouch should >= 5px
                logger.info('Swipe distance < 10px, dropped')
                return

        if method == 'minitouch':
            self.swipe_minitouch(p1, p2)
        elif method == 'ADB':
            self.swipe_adb(p1, p2)
