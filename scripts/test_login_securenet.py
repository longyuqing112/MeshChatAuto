# SecureNetAutoWin/script/test_login_securenet.py
import os
import time

import pytest
import redis
# from pymongo import MongoClient
from selenium.common import TimeoutException

from conftest import driver
from pages.windows.loc.login_locators import ERROR_ALERT, PHONE_ERROR_TIP, PASSWORD_ERROR_TIP
from pages.windows.log_out_page import LogOutPage
from pages.windows.login_securenet_page import LoginPage
# from utils.config_yaml_utils import YamlConfigUtils
# 修改为（使用新的config_utils）
from utils.config_utils import ConfigUtils  # 注意类名大小写需与实际一致

from selenium.webdriver.common.by import By
from  selenium.webdriver.support import  expected_conditions as EC

current_dir = os.path.dirname(__file__)
# 拼接 YAML 文件的绝对路径
yaml_file_path = os.path.abspath(os.path.join(current_dir, "../data/login_test_data.yaml"))

def load_test_data(file_path):
    yaml_utils = ConfigUtils(file_path)
    print("当前工作目录:", os.getcwd())
    print("YAML 文件路径:", yaml_file_path)
    # return yaml_utils.load_yaml_test_data()  # ← 这里返回的是未渲染的原始数据
    return yaml_utils.read_config(render_vars=True)  # 关键！启用模板渲染


def asset_login_result(login_page,test_data):
    alert_expected = test_data.get("expected", {}).get("alert_expected")
    expected_phone_tip = test_data.get("expected", {}).get("tip_expected")
    login_success = test_data.get("expected",{}).get("login_success",False) #默认为False
    # 用户名或密码错误的情况
    # if "alert_expected" in test_data["expected"]:
    if alert_expected:
        try:
            # 等待顶部弹窗出现
            login_page.wait.until(EC.visibility_of_element_located(ERROR_ALERT))
            print("顶部弹窗已出现，等待弹窗消失...")
            # 获取弹窗文本
            actual_alert = login_page.base_get_text_with_js_wait(ERROR_ALERT)
            print("顶部的实际的结果是：", actual_alert)
            assert actual_alert == test_data["expected"][
                "alert_expected"], f"预期 error message: {test_data['expected']['alert_expected']}, but 实际是: {actual_alert}"
            login_page.wait.until(EC.invisibility_of_element_located(PHONE_ERROR_TIP))
            print("弹窗已消失，继续执行后续步骤...")
        except TimeoutException:
            raise AssertionError("顶部弹窗未出现或未正确关闭")
    # if "tip_expected" in test_data["expected"]:
    if expected_phone_tip:
        # 根据用户名或密码的错误提示进行断
        if test_data.get("username", "") == "":
            # 手机号为空的情况
            actual_phone_tip = login_page.base_get_text(PHONE_ERROR_TIP)
            assert actual_phone_tip == test_data["expected"][
                "tip_expected"], f"预期 phone error message: {test_data['expected']['tip_expected']}, but 实际是: {actual_phone_tip}"
        elif test_data.get("password", "") == "":
            # 密码为空的情况
            actual_password_tip = login_page.base_get_text(PASSWORD_ERROR_TIP)
            assert actual_password_tip == test_data["expected"][
                "tip_expected"], f"预期 password error message: {test_data['expected']['tip_expected']}, but 实际是: {actual_password_tip}"
    #判断登入成功的断言
    if login_success:
        try:
            login_page.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "main.h-screen.w-screen.flex"))
            )
            time.sleep(3)
            print("登录成功，页面结构符合预期")
            login_page.handle_close_popup()# 调用处理弹窗的函数

            logout_page = LogOutPage(login_page.driver)
            logout_page.open_logout_dialog()
            logout_page.click_confirm()
            print("已执行退出登录操作")


        except TimeoutException:
            raise AssertionError("登录失败，未找到登录成功后的页面结构")





# 登录测试用例，不需要自动登录
@pytest.mark.no_auto_login
@pytest.mark.parametrize("test_data",load_test_data(yaml_file_path)["test_suites"]["username_password"])
def test_login_number(driver, test_data):
    """使用 YAML 文件中的测试数据执行登录测试"""
    login_page = LoginPage(driver)

    login_page.login(
        phonenumber=test_data.get("username",""),
        password=test_data.get("password",""),

        remember=test_data.get("remember",True),
        terms_agree=test_data.get("terms",True)
    )
    asset_login_result(login_page,test_data)
# #

#
#
# # 登录测试用例，不需要自动登录
# @pytest.mark.no_auto_login
# @pytest.mark.parametrize("test_data",load_test_data(yaml_file_path)["test_suites"]["environment_selection"])
# def test_login_securenet(driver, test_data):
#     """使用 YAML 文件中的测试数据执行登录测试"""
#     login_page = LoginPage(driver)
#     login_page.login(
#         phonenumber=test_data.get("username",""),
#         password=test_data.get("password",""),
#         env=test_data.get("env","Local"),
#         remember=test_data.get("remember",True),
#         terms_agree=test_data.get("terms",True)
#     )
#     asset_login_result(login_page, test_data)
#
# #
# @pytest.mark.order(3)
# # 登录测试用例，不需要自动登录
# @pytest.mark.no_auto_login
# @pytest.mark.parametrize("test_data",load_test_data(yaml_file_path)["test_suites"]["checkbox_combinations"])
# def test_checkbox_combinations(driver, test_data):
#         """使用 YAML 文件中的测试数据执行复选框组合测试"""
#         login_page = LoginPage(driver)
#         login_page.login(
#         phonenumber=test_data.get("username", ""),
#         password=test_data.get("password",""),
#         env=test_data.get("env", "Local"),
#         remember=test_data.get("remember", True),
#         terms_agree=test_data.get("terms", True)
#         )
#         time.sleep(1)
#         asset_login_result(login_page, test_data)

def load_multi_accounts():
    config = ConfigUtils(yaml_file_path).read_config(render_vars=True)
    return config["test_suites"]["multi_account_login"]


# @pytest.mark.no_auto_login
# def test_multi_account_login(driver):
#     """多账号同时登录测试"""
#     accounts = load_multi_accounts()
#     drivers = []
#     login_page = LoginPage(driver)
#
#     try:
#         # 创建多个实例并登录
#         for i, account in enumerate(accounts):
#             driver = login_page.start_app(instance_id=i)
#             drivers.append(driver)
#
#             login_page = LoginPage(driver)
#             login_page.login(
#                 phonenumber=account["username"],
#                 password=account["password"],
#                 env=account.get("env", "Local"),
#                 remember=account.get("remember", True),
#                 terms_agree=account.get("terms", True)
#             )
#
#             # 验证登录成功
#             login_page.wait.until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "main.h-screen.w-screen.flex"))
#             )
#             time.sleep(1)
#             login_page.handle_close_popup()
#
#             print(f"账号 {account['username']} 登录成功")
#
#         # 在这里添加多账号交互测试逻辑
#         time.sleep(5)  # 保持登录状态
#
#     finally:
#         # 确保所有实例都被关闭
#         for driver in drivers:
#             try:
#                 driver.quit()
#             except:
#                 pass