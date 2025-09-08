import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from  selenium.webdriver.support import  expected_conditions as EC

from pages.windows.log_out_page import LogOutPage
from pages.windows.login_securenet_page import LoginPage



# 登录测试用例，不需要自动登录
@pytest.mark.no_auto_login
def test_logout_cancel(driver):
    login_page = LoginPage(driver)

    login_page.login(
        phonenumber='19911111111',
        password='111111a',
        env='Local',
        remember='True',
        terms_agree='True'
    )
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "main.h-screen.w-screen.flex"))
    )
    time.sleep(2)
    login_page.handle_close_popup()  # 调用处理弹窗的函数

    logout_page = LogOutPage(driver)
    logout_page.open_logout_dialog()

    logout_page.click_confirm()

    try:
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "main.h-screen.w-screen.flex"))
        )
        print("注销成功，登录界面消失了。")
        # #发消息保持登入
        # login_page = LoginPage(driver)
        #
        # login_page.login(
        #     phonenumber='19911111111',
        #     password='111111a',
        #     env='Local',
        #     remember='True',
        #     terms_agree='True'
        # )
        # WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, "main.h-screen.w-screen.flex"))
        # )
        # time.sleep(2)
        # login_page.handle_close_popup()  # 调用处理弹窗的函数

    except Exception as e:
        raise AssertionError("注销失败，登录界面仍然可见。") from e

