#SecureNetWin/conftest.py
import time
# from lib2to3.pgen2.tokenize import group

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from pages.windows.log_out_page import LogOutPage
from pages.windows.login_securenet_page import LoginPage
from utils.app_utils import start_securenet_win_app
from  selenium.webdriver.support import  expected_conditions as EC

@pytest.fixture(scope="session")
def driver():
    driver = start_securenet_win_app()
    yield driver
    time.sleep(10)
    driver.quit()


def pytest_collection_modifyitems(config, items):
    """控制测试用例执行顺序"""
    test_order = {
        'test_open_app':0,
        'test_login_securenet': 1,
        'test_log_out': 2,
        'test_message_text': 3
    }

    def get_test_order(item):
        # 提取文件名，而不是测试方法名
        test_file = item.nodeid.split('::')[0].split('/')[-1].replace('.py', '')
        print(f"Processing test file: {test_file}")  # 调试输出
        return test_order.get(test_file, 999)

    print("Before sorting:")  # 调试输出
    for item in items:
        print(item.nodeid)

    # 按照提取的文件名排序
    items.sort(key=get_test_order)

    print("\nAfter sorting:")  # 调试输出
    for item in items:
        print(item.nodeid)

#
@pytest.fixture(autouse=True,scope="session")
def auto_login(request,driver):
    # 检查测试用例是否标记为 no_auto_login
    if 'no_auto_login' not in request.keywords:
        # 执行登录操作
        login_page = LoginPage(driver)
        login_page.login(
            phonenumber='19911111111',
            password='111111a',
            firm='MESH',
            env='Local',
            remember='True',
            terms_agree='True'
        )
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "main.h-screen.w-screen.flex"))
        )
        time.sleep(2)
        login_page.handle_close_popup()
        # logout_page = LogOutPage(driver)
        # logout_page.open_logout_dialog()
        # logout_page.click_confirm()
        yield


    else:
        # 如果标记为 no_auto_login，则跳过登录
        yield

# @pytest.fixture
# def auto_login(driver, clean_state):
#     """提供已登录状态的会话"""
#     login_page = LoginPage(driver)
#     if not is_logged_in(driver):  # 需要实现这个检查函数
#         login_page.login(
#             phonenumber='15727576786',
#             password='15727576786',
#             env='Local',
#             remember='True',
#             terms_agree='True'
#         )
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "main.h-screen.w-screen.flex"))
#         )  # 这里补全了括号
#         login_page.handle_close_popup()  # 现在是独立的语句
#     yield
#     # 不自动登出，保持登录状态供后续用例使用
#
# def is_logged_in(driver):
#     """检查当前是否已登录"""
#     try:
#         return bool(driver.find_elements(By.CSS_SELECTOR, ".h-screen.w-screen.flex"))
#     except:
#         return False