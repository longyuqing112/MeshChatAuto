import os
import time

import pytest

from pages.windows.block_friend_page import BlockMessagePage
from utils.config_utils import ConfigUtils
from utils.config_yaml_utils import YamlConfigUtils
from utils.mul_login import MultiInstanceManager

current_dir = os.path.dirname(__file__)
# 拼接 YAML 文件的绝对路径
yaml_file_path = os.path.abspath(os.path.join(current_dir, "../data/message_data.yaml"))
base_dir = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.abspath(os.path.join(base_dir, "../"))

print(yaml_file_path,'定位路径')


def load_test_data(file_path,render_vars=True):
    """
        加载测试数据，支持模板变量渲染
    """
    config_utils = ConfigUtils(yaml_file_path)
    return config_utils.read_config(render_vars=render_vars)
    # yaml_utils = YamlConfigUtils(file_path)
    # data = yaml_utils.load_yaml_test_data()
    # return {
    #     'block_friend_tests': data.get('block_friend_tests', [])
    # }

def load_multi_accounts():
    config = ConfigUtils(yaml_file_path).read_config(render_vars=True)
    return  config["block_friend_tests"]

@pytest.mark.parametrize(
    "test_case",load_test_data(yaml_file_path,render_vars=True)['block_friend_tests'],
)
def test_block_friend_workflow(driver,auto_login,test_case):
    sender_page = BlockMessagePage(driver)
    # 1. 初始化多实例管理器
    instance_manager = MultiInstanceManager(driver)
    # 2. 加载测试账号配置
    accounts = load_multi_accounts()
    receiver_account = next(a for a in accounts if a['role'] == "receiver_b")
    try:
        # 3. 当前driver是主测试账号(sender)，无需重新登录
        sender_page.block_friend(target='friend',
                                 phone=receiver_account['username'],
                                 actions =test_case['actions'],
                                 instance_manager = instance_manager,
                                 receiver_account=receiver_account,
                                 sender=test_case['sender']
                                 )
    finally:
        time.sleep(3)
        # 清理附加实例
        instance_manager.cleanup()