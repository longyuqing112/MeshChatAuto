import os
import time

import pytest

from conftest import driver
from pages.windows.friend_operation_page import FriendOperationPage
from pages.windows.login_securenet_page import LoginPage
from utils.config_utils import ConfigUtils
from utils.config_yaml_utils import YamlConfigUtils
from utils.mul_login import MultiInstanceManager

current_dir = os.path.dirname(__file__)
# 拼接 YAML 文件的绝对路径
yaml_file_path = os.path.abspath(os.path.join(current_dir, "../data/message_data.yaml"))
base_dir = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.abspath(os.path.join(base_dir, "../"))

print(yaml_file_path,'定位路径')


def load_test_data(file_path):
    yaml_utils = YamlConfigUtils(file_path)
    data = yaml_utils.load_yaml_test_data()
    return {
        'add_friend_tests': data.get('add_friend_tests', []),
        'accept_friend_tests': data.get('accept_friend_tests', []),
    }

#
# @pytest.mark.parametrize(
#     "test_case", load_test_data(yaml_file_path)['add_friend_tests'],
#     ids=lambda case: case['name']  # 用测试名称作为用例ID
# )
# def test_add_friend_operation(driver,test_case,auto_login):
#     friend_operation_page = FriendOperationPage(driver)
#     if test_case['method'] == "menu":
#         friend_operation_page.add_via_menu (
#             identifier = test_case['identifier']
#         )
#     elif test_case['method'] == "global":
#         friend_operation_page = FriendOperationPage(driver)
#         friend_operation_page.add_via_global_search(
#             identifier=test_case['identifier']
#         )
# def test_delete_friend_operation(driver):
#     friend_operation_page = FriendOperationPage(driver)
#     target_friend = 'LYQ003'
#     # 先测试取消删除的情况
#     print("\n=== 测试取消删除好友 ===")
#     friend_operation_page.delete_friend(
#         phone=target_friend,confirm=False
#     )
#     is_friend_exist = friend_operation_page.scroll_to_friend_in_contacts(target_friend, raise_exception=False)
#     assert is_friend_exist, f"取消删除后，好友 {target_friend} 应该仍在联系人列表中"
#     print(f"验证成功：取消删除后，好友 {target_friend} 仍在联系人列表中")
#
#     # 再测试确认删除的情况
#     print("\n=== 测试确认删除好友 ===")
#     friend_operation_page.delete_friend(phone=target_friend, confirm=True)
#
#     # 验证确认删除后好友已不在
#     is_friend_exist = friend_operation_page.scroll_to_friend_in_contacts(target_friend, raise_exception=False)
#     assert not is_friend_exist, f"确认删除后，好友 {target_friend} 应该已从联系人列表中移除"
#     print(f"验证成功：确认删除后，好友 {target_friend} 已从联系人列表中移除")
#
# #————————删除好友请求数据
# def test_delete_friend_request(driver):
#     friend_operation_page = FriendOperationPage(driver)
#     friend_operation_page.delete_friend_request(confirm=False)
#     time.sleep(2)
#     friend_operation_page.delete_friend_request(confirm=True)
#
# #————————接受好友数据
# @pytest.mark.parametrize(
#     "test_case", load_test_data(yaml_file_path)['accept_friend_tests'],
#     ids=lambda case: case['name']  # 用测试名称作为用例ID
# )
# def test_accept_friend_operation(driver,test_case,auto_login):
#     friend_operation_page = FriendOperationPage(driver)
#     friend_operation_page.accept_friend_operation(
#         identifier = test_case['identifier'],
#         action = test_case['action']
#     )
#
def load_multi_accounts():
    config = ConfigUtils(yaml_file_path).read_config(render_vars=True)
    return  config["multi_account_login"]



def test_complete_friend_workflow(driver,auto_login):
    # 1. 初始化多实例管理器
    instance_manager = MultiInstanceManager(driver)
    # 2. 加载测试账号配置

    accounts = load_multi_accounts()
    sender_account = next(a for a in accounts if a['role'] == "sender")
    receiver_b_account =  next(a for a in accounts if a['role'] == "receiver_b")
    receiver_c_account = next(a for a in accounts if a['role'] == "receiver_c")
    try:
        # 3. 当前driver是主测试账号(sender)，无需重新登录
        sender_page = FriendOperationPage(driver)
        # 4. sender添加receiver为好友
        sender_page.add_via_global_search(receiver_b_account["username"])
        time.sleep(2)

        # 5. 启动receiver实例
        print("\n=== 启动receiver实例 ===")
        receiver_b_driver = instance_manager.start_receiver_instance(receiver_b_account)
        receiver_b_page = FriendOperationPage(receiver_b_driver)

        # 6. receiver拒绝好友申请

        print("\n=== receiver拒绝好友请求 ===")
        receiver_b_page.accept_friend_operation(
            identifier=sender_account["username"],
            action="reject"
        )

        # 7. sender再次添加receiver为好友
        print("\n=== sender再次发送好友请求 ===")
        sender_page.add_via_global_search(receiver_b_account["username"])

        # 8. receiver接受好友申请
        print("\n=== receiver接受好友请求 ===")
        receiver_b_page.accept_friend_operation(
            identifier=sender_account["username"],
            action="accept"
        )

        # 9. 验证好友关系
        print("\n===  验证好友关系 ===")
        time.sleep(2)
        # 刷新联系人列表
        sender_page.open_menu_panel("contacts")  # 重新打开联系人面板
        assert sender_page.scroll_to_friend_in_contacts(
            receiver_b_account["username"],
            raise_exception=False
        ),"sender联系人列表中找不到receiver"

        assert receiver_b_page.scroll_to_friend_in_contacts(
            sender_account["username"],
            raise_exception=False
        ),"receiver联系人列表中找不到sender"
        # 插一条
        print("\n=== 取消删除好友 ===")
        sender_page.delete_friend(
            phone=receiver_b_account,
            confirm=False
        )
        #验证取消删除
        assert  sender_page.scroll_to_friend_in_contacts(
            receiver_b_account["username"],
            raise_exception=False
        )


        # 10. sender删除receiver好友
        print("\n=== sender删除好友 ===")
        sender_page.delete_friend(phone=receiver_b_account["username"],confirm=True)

        # 11. 验证删除成功
        print("\n=== 验证删除成功 ===")
        assert  not sender_page.scroll_to_friend_in_contacts(
            receiver_b_account["username"],
            raise_exception=False
        ),"删除后sender联系人列表仍能找到receiver"
        # 10.3 receiver删除sender 满足双向删除
        print("=== receiver删除sender ===")
        receiver_b_page.delete_friend(phone=sender_account["username"], confirm=True)

        # 10.4 验证receiver侧删除
        assert not receiver_b_page.scroll_to_friend_in_contacts(
            sender_account["username"],
            raise_exception=False
        ), "删除后receiver联系人列表仍能找到sender"

        print("\n=== 双向删除验证成功 ===")

        # ===== Test with Receiver C =====
        print("\n===测试A单项删除B ===")
        sender_page.delete_friend(
            phone=receiver_c_account["username"],
            confirm=True
        )
        # 11. 验证单项删除成功
        assert not sender_page.scroll_to_friend_in_contacts(
            receiver_c_account["username"],
            raise_exception=False
        ), "删除后sender联系人列表仍能找到receiver"

        #A单项添加C
        sender_page.add_via_menu(receiver_c_account["username"])
        # 8. receiver接受好友申请
        assert sender_page.scroll_to_friend_in_contacts(
            receiver_c_account["username"],
            raise_exception=False
        )


    finally:
        time.sleep(3)
        # 清理附加实例
        instance_manager.cleanup()



