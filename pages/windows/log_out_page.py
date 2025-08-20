from selenium.webdriver.support.wait import WebDriverWait

from base.electron_pc_base import ElectronPCBase
from pages.windows.loc.settings_locators import SETTINGS_LOGO, DIALOG_CONTAINER, LOG_OUT_BUTTON, DIALOG_CONFIRM_BUTTON, \
    DIALOG_CANCEL_BUTTON


class LogOutPage(ElectronPCBase):
    def __init__(self, driver):
        super().__init__()  # 调用父类构造函数
        self.driver = driver  # 设置 driver
        self.wait = WebDriverWait(driver, 10, 0.5)  # 初始化 wait

    def open_logout_dialog(self):
        self.base_click(SETTINGS_LOGO)
        self.base_click(LOG_OUT_BUTTON)
        self.base_find_element(DIALOG_CONTAINER)
    def click_cancel(self):
        self.base_click(DIALOG_CANCEL_BUTTON)

    def click_confirm(self):
        self.base_click(DIALOG_CONFIRM_BUTTON)


