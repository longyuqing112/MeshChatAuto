import os
import time
from selenium.webdriver.common.by import By
from pages.windows.login_securenet_page import LoginPage
from utils.config_utils import ConfigUtils
from  selenium.webdriver.support import  expected_conditions as EC
import  pytest
current_dir = os.path.dirname(__file__)
# 拼接 YAML 文件的绝对路径
yaml_file_path = os.path.abspath(os.path.join(current_dir, "../data/login_test_data.yaml"))

class MultiInstanceManager:
    def __init__(self,main_driver=None):
        self.main_driver = main_driver
        self.additional_driver = None

    def start_receiver_instance(self,account_data, instance_id=1):
        """启动接收者实例并登录"""
        if self.additional_driver:
            return self.additional_driver
        login_page = LoginPage(None)
        try:
            # 启动新实例
            driver = login_page.start_app(instance_id=instance_id)
            # 登入接收者账号
            login_page = LoginPage(driver)
            login_page.login(
                phonenumber=account_data["username"],
                password=account_data["password"],
                env=account_data.get("env", "Local"),
                remember=account_data.get("remember", True),
                terms_agree=account_data.get("terms", True)
            )
            # 验证登录成功
            login_page.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "main.h-screen.w-screen.flex"))
            )
            time.sleep(1)
            login_page.handle_close_popup()
            self.additional_driver = driver
            print(f"接收者实例登录成功 - 账号: {account_data['username']}")
            return driver
        except Exception as e:
            print(f"启动接收者实例失败: {str(e)}")
            if driver:
                driver.quit()
            raise
    def cleanup(self):
        """清理附加实例"""
        if self.additional_driver:
            try:
                self.additional_driver.quit()
                print("已关闭接收者实例")
            except Exception as e:
                print(f"关闭接收者实例时出错: {str(e)}")
            self.additional_driver = None