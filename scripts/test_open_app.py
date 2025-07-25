
import pytest

from pages.windows.login_securenet_page import LoginPage

@pytest.mark.no_auto_login
def test_open_app(driver):
    """
    测试 Electron 应用是否能够成功启动
    """
    assert driver.title == "SecureNet"
