from datetime import datetime, timezone, timedelta
from functools import cached_property

from module.base.timer import Timer
from module.base.utils import point2str
from module.gift.assets import *
from module.handler.assets import ANNOUNCEMENT
from module.logger import logger
from module.ui.assets import MAIN_GOTO_CASH_SHOP, MAIN_CHECK, GOTO_BACK, CASH_SHOP_CHECK
from module.ui.page import page_main
from module.ui.ui import UI


class NetworkError(Exception):
    pass


class GiftBase(UI):
    diff = datetime.now(timezone.utc).astimezone().utcoffset() - timedelta(hours=8)

    def _run(self, button, check):
        if not self.appear(CASH_SHOP_CHECK, offset=(10, 10)):
            self.ui_ensure(page_main)
        try:
            self.ensure_into_shop()
            self.receive_available_gift(button, check)
        except NetworkError:
            logger.error('Cannot access the cash shop under the current network')
            logger.error("If you haven't logged into Google Play, please log in and try again.")
            self.ensure_back()

    def ensure_into_shop(self, skip_first_screenshot=True):
        confirm_timer = Timer(1, count=2).start()
        click_timer = Timer(0.3)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() and self.appear_then_click(MAIN_GOTO_CASH_SHOP, offset=(30, 30), interval=2):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.appear_then_click(GOTO_GENERAL_GIFT, offset=(30, 30), interval=6,
                                                                static=False):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.handle_popup():
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() \
                    and self.appear(GENERAL_GIFT_CHECK, offset=(10, 10), static=False) \
                    and not self.appear(MONTHLY, offset=(10, 10), static=False):
                self.ensure_sroll((590, 360), (300, 360), 1, 0.4)
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.appear(GENERAL_GIFT_CHECK, offset=(10, 10), static=False) and confirm_timer.reached():
                break

            if click_timer.reached() and self.appear(FAILED_CHECK, offset=(30, 30), static=False):
                raise NetworkError

    def receive_available_gift(self, button, check, skip_first_screenshot=True):
        confirm_timer = Timer(3, count=2).start()
        click_timer = Timer(0.3)
        button_click_count = 0
        max_button_clicks = 5  # Maximum attempts to click the button
        
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() and self.handle_popup():
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.appear_then_click(button, offset=(30, 30), interval=2):
                button_click_count += 1
                logger.info(f"Clicked {button.name} ({button_click_count}/{max_button_clicks})")
                confirm_timer.reset()
                click_timer.reset()
                
                # Exit if clicked too many times
                if button_click_count >= max_button_clicks:
                    logger.info(f"Reached maximum clicks for {button.name}, assuming already collected")
                    break
                continue

            # Check if already collected (the check button is visible)
            if self.appear(check, offset=5, static=False):
                if confirm_timer.reached():
                    logger.info(f"Gift already collected, {check.name} detected")
                    break
                elif button_click_count == 0:
                    # If we haven't clicked yet and see the check, it's already collected
                    logger.info(f"Gift already collected, {check.name} visible on first check")
                    break

        skip_first_screenshot = True
        confirm_timer.reset()
        click_timer.reset()
        gift_click_count = 0
        max_gift_clicks = 3  # Maximum attempts to click GIFT

        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() \
                    and self.appear(GIFT, offset=5, static=False, interval=2) \
                    and GIFT.match_appear_on(self.device.image, threshold=25):
                gift_click_count += 1
                logger.info(f"Clicked GIFT ({gift_click_count}/{max_gift_clicks})")
                self.device.click(GIFT)
                click_timer.reset()
                confirm_timer.reset()
                
                # Exit if clicked too many times
                if gift_click_count >= max_gift_clicks:
                    logger.info(f"Reached maximum GIFT clicks, assuming collection complete")
                    break
                continue

            if click_timer.reached() and self.handle_popup():
                confirm_timer.reset()
                click_timer.reset()
                continue

            if click_timer.reached() and self.handle_reward(1):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.appear(GOTO_BACK, offset=5, static=False) and confirm_timer.reached():
                logger.info("GOTO_BACK detected, gift collection complete")
                break
                
            # Additional timeout check after at least one GIFT click
            if gift_click_count > 0 and confirm_timer.reached():
                logger.info("Timeout reached after gift collection")
                break

    def ensure_back(self, skip_first_screenshot=True):
        confirm_timer = Timer(2, count=2).start()
        click_timer = Timer(0.3)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if click_timer.reached() and self.appear_then_click(ANNOUNCEMENT, offset=(30, 30), interval=3,
                                                                static=False):
                confirm_timer.reset()
                click_timer.reset()
                continue

            if self.appear(MAIN_CHECK, offset=(30, 30), static=False) and confirm_timer.reached():
                break


class DailyGift(GiftBase):
    def run(self):
        self._run(DAILY, DAILY_CHECK)
        self.config.task_delay(server_update=True)


class WeeklyGift(GiftBase):

    @property
    def next_tuesday(self) -> datetime:
        local_now = datetime.now()
        # weekday() returns 0 for Monday, 1 for Tuesday, etc.
        # We want to find the next Tuesday (1)
        days_until_tuesday = (1 - local_now.weekday()) % 7
        # If today is Tuesday and we've already run, schedule for next week
        if days_until_tuesday == 0:
            days_until_tuesday = 7
        next_tuesday = local_now.replace(hour=4, minute=0, second=0, microsecond=0) + timedelta(days=days_until_tuesday)
        # Make sure we're scheduling for the future
        if next_tuesday <= local_now:
            next_tuesday += timedelta(days=7)
        return next_tuesday + self.diff

    def run(self):
        self._run(WEEKLY, WEEKLY_CHECK)
        # Always schedule for next week to avoid running repeatedly
        self.config.task_delay(minute=10080)  # 7 days = 10080 minutes


class MonthlyGift(GiftBase):

    @property
    def next_month(self) -> datetime:
        local_now = datetime.now()
        # Calculate next month
        if local_now.month == 12:
            next_month = 1
            next_year = local_now.year + 1
        else:
            next_month = local_now.month + 1
            next_year = local_now.year
        
        next_month_date = local_now.replace(year=next_year, month=next_month, day=1, hour=4, minute=0, second=0, microsecond=0)
        
        # If we're already past the 1st at 4:00 AM this month, ensure we don't schedule for the past
        current_month_date = local_now.replace(day=1, hour=4, minute=0, second=0, microsecond=0)
        if local_now.day == 1 and local_now < current_month_date:
            # It's the 1st but before 4 AM, so we can run today
            return current_month_date + self.diff
        
        return next_month_date + self.diff

    def run(self):
        self._run(MONTHLY, MONTHLY_CHECK)
        # Always schedule for next month (30 days) to avoid running repeatedly
        self.config.task_delay(minute=43200)  # 30 days = 43200 minutes
