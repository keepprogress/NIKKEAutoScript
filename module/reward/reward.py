from module.base.timer import Timer
from module.handler.assets import CONFIRM_B
from module.logger import logger
from module.reward.assets import *
from module.ui.page import *
from module.ui.ui import UI


class NoRewards(Exception):
    pass


class Reward(UI):
    def receive_reward(self, skip_first_screenshot=True):
        logger.hr("Receive reward")
        confirm_timer = Timer(1, count=3).start()
        # Set click interval to 0.3, because game can't respond that fast.
        click_timer = Timer(0.3)
        receive_count = 0
        max_receive_clicks = 3  # Exit after clicking RECEIVE 3 times
        
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if self.handle_level_up(interval=1):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.handle_reward(interval=1):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.handle_paid_gift():
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.appear_then_click(
                    RECEIVE, offset=(30, 30), interval=10
            ):
                receive_count += 1
                logger.info(f"Clicked RECEIVE ({receive_count}/{max_receive_clicks})")
                confirm_timer.reset()
                click_timer.reset()
                
                # Exit after clicking RECEIVE max times
                if receive_count >= max_receive_clicks:
                    logger.info(f"Reached maximum RECEIVE clicks ({max_receive_clicks}), assuming rewards collected")
                    break
                continue
            
            # Try to detect EMPTY_CHECK but don't rely on it
            try:
                if self.appear(EMPTY_CHECK, threshold=1.00):
                    logger.info("Detected EMPTY_CHECK, no more rewards")
                    break
            except:
                pass

            # Also check for MAIN_CHECK as a fallback
            try:
                if self.appear(MAIN_CHECK, offset=(10, 10)) and confirm_timer.reached():
                    logger.info("Back at main screen, rewards collection complete")
                    break
            except:
                pass
                
            # Additional timeout check - if we haven't clicked anything for a while
            if confirm_timer.reached() and receive_count > 0:
                logger.info("Timeout reached after collecting rewards")
                break

        logger.info("Defence Reward have been received")
        return True

    def receive_social_point(self, skip_first_screenshot=True):
        logger.hr("Receive social point")
        confirm_timer = Timer(5, count=3).start()
        click_timer = Timer(0.3)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() and self.appear_then_click(
                    SEND_AND_RECEIVE, offset=(30, 30), interval=2
            ):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.appear_then_click(
                    CONFIRM_B, offset=(30, 30), interval=1, static=False
            ):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if confirm_timer.reached():
                break

        logger.info("Social Point have been received")
        return True

    def receive_special_arena_point(self, skip_first_screenshot=True):
        logger.hr("Receive special arena point")
        confirm_timer = Timer(6, count=5).start()
        click_timer = Timer(0.3)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() and self.appear_then_click(
                    ARENA_GOTO_SPECIAL_ARENA, offset=(30, 30), interval=5, static=False
            ):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.appear_then_click(
                    RECEIVE_SPECIAL_ARENA_POINT, offset=(30, 30), interval=5, static=False
            ):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.appear_then_click(
                    REWARD_B, offset=(30, 30), interval=5, static=False
            ):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.appear(NO_REWARDS, offset=(5, 5), threshold=0.95, static=False):
                raise NoRewards

            elif self.appear(NO_REWARDS_2, offset=(5, 5), threshold=0.95, static=False):
                return True

            elif self.appear(NO_REWARDS_3, offset=(5, 5), threshold=0.95):
                return True

            if self.handle_reward(interval=1):
                logger.info("Special Arena Point have been received")
                raise NoRewards

            if confirm_timer.reached():
                raise NoRewards

        return True

    def ensure_back(self, skip_first_screenshot=True):
        click_timer = Timer(0.3)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() and self.handle_reward(interval=1):
                click_timer.reset()
                continue

            if self.appear(SPECIAL_ARENA_CHECK, offset=(5, 5), static=False):
                break

            if click_timer.reached():
                # Click back button area (top-left corner)
                from module.base.button import Button
                back_button = Button(area=(50, 50, 150, 150), color=(0, 0, 0), button=(50, 50, 150, 150))
                self.device.click(back_button)
                click_timer.reset()

    def temporary(self, button, skip_first_screenshot=True):
        click_timer = Timer(0.3)
        confirm_timer = Timer(1, count=2).start()
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() and self.appear_then_click(
                    button, offset=(5, 5), interval=0.3, static=False, threshold=0.9
            ):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if confirm_timer.reached():
                break

    def run(self):
        self.ui_ensure(page_reward)
        self.receive_reward()
        if self.config.Reward_CollectSocialPoint:
            # ----
            # self.ui_ensure(page_friend)
            # ----
            self.ui_ensure(page_main)
            self.temporary(MAIN_GOTO_FRIEND)
            # ----
            self.receive_social_point()
        if self.config.Reward_CollectSpecialArenaPoint:
            self.ui_ensure(page_arena)
            try:
                self.receive_special_arena_point()
            except NoRewards:
                self.ensure_back()
        self.config.task_delay(server_update=True)