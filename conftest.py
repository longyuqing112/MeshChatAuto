# SecureNetWin/conftest.py
import os
import time
# from lib2to3.pgen2.tokenize import group

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from pages.windows.create_group_page import GroupPage
from pages.windows.loc.message_locators import SELECT_CLOSE
from pages.windows.log_out_page import LogOutPage
from pages.windows.login_securenet_page import LoginPage
from utils.app_utils import start_securenet_win_app
from selenium.webdriver.support import expected_conditions as EC
from pages.windows.msg_actions_page import MsgActionsPage
from utils.config_utils import ConfigUtils
from utils.mul_login import MultiInstanceManager
from utils.random_utils import generate_random_id
from utils.dir_utils import resolve_media_paths

current_dir = os.path.dirname(__file__)
yaml_file_path = os.path.abspath(os.path.join(current_dir, "./data/group_data.yaml"))


def load_test_data(file_path, render_vars=True):
    """
        加载测试数据，支持模板变量渲染
    """
    config_utils = ConfigUtils(file_path)
    return config_utils.read_config(render_vars=render_vars)


def load_multi_accounts():
    config = ConfigUtils(yaml_file_path).read_config(render_vars=True)
    return config["create_group"]


@pytest.fixture(scope="session")
def driver():
    driver = start_securenet_win_app()
    yield driver
    time.sleep(10)
    driver.quit()


def pytest_collection_modifyitems(config, items):
    """控制测试用例执行顺序"""
    test_order = {
        'test_open_app': 0,
        'test_message_text': 1,
        'test_msg_actions': 2,        # 消息操作测试
        'test_card_message.py': 3,
        'test_friend_opration.py':4,
        'test_other_features': 5,
        'test_block_friend.py': 6,
        'test_create_group.py': 7,
        'test_log_out.py': 99,

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
@pytest.fixture(autouse=True, scope="session")
def auto_login(request, driver):
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
        print("=== 自动登录完成，开始执行测试用例 ===")
        # 在这里yield，所有测试用例会在这个点之后执行
        yield

        # 所有测试用例执行完毕后执行退出登录

        # print("=== 所有测试执行完毕，开始退出登录 ===")
        # try:
        #     logout_page = LogOutPage(driver)
        #     logout_page.open_logout_dialog()
        #     logout_page.click_confirm()
        #     print("退出登录成功")
        # except Exception as e:
        #     print(f"退出登录失败: {e}")
        # print("=== 退出登录完成 ===")

    else:
        # 如果标记为 no_auto_login，则跳过登录
        yield


import pytest


@pytest.fixture(scope="session", autouse=False)
def clear_favorites_once(driver):
    action_page = MsgActionsPage(driver)
    try:
        success = action_page.clear_favorites()
        if not success:
            print("清空收藏操作返回失败，但继续执行测试")
        print("收藏列表清空完成")
        action_page.open_menu_panel('home')
        close_buttons = driver.find_elements(*SELECT_CLOSE)  # 使用 find_elements 判断是否存在
        if close_buttons:  # 如果列表不为空，说明元素存在
            close_button = close_buttons[0]  # 取第一个（如果有多个匹配也只处理第一个）
            close_button.click()
            print("检测到关闭按钮并已点击")
    except Exception as e:
        print(f"清空收藏时发生异常: {e}，继续执行测试")


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


@pytest.fixture(scope="module")  # 改为 module scope，只在群聊模块内共享
def shared_group_setup_teardown(driver, auto_login):
    """群聊模块的setup和teardown：创建群聊 → 执行所有群聊测试 → 清理"""
    print("=== 开始群聊模块 setup ===")
    # 获取测试数据
    test_data = load_test_data(yaml_file_path, render_vars=True)['create_group']
    test_case = test_data[0]  # 使用第一个测试用例数据
    target_phone = test_case['target_phone']
    select_count = test_case['select_count']
    # 创建实例
    group_page = GroupPage(driver)
    instance_manager = MultiInstanceManager(driver)
    # 生成唯一的群组名称
    test_id = generate_random_id(5)
    group_name = f"{test_case['group_name']}[ID:{test_id}]"
    search_queries = test_case['search_queries']
    inviter_number = test_case['creator_number']
    print(f"创建共享群聊: {group_name}")
    # 创建群聊
    expected_member_count = group_page.create_group(
        message_content=group_name,
        search_queries=test_case['search_queries'],
    )
    # 验证成员接收
    accounts = load_multi_accounts()
    member_account = next(a for a in accounts)
    group_page.verify_member_receiver(instance_manager,
                                      member_account,
                                      group_name,
                                      expected_member_count,
                                      search_queries,
                                      inviter_number)

    # 提前处理消息路径
    all_msg = test_case['messages'].copy()
    processed_msg = all_msg.copy()

    if 'image_paths' in processed_msg and processed_msg['image_paths']:
        processed_msg['image_paths'] = resolve_media_paths(processed_msg['image_paths'])

    if 'file_paths' in processed_msg and processed_msg['file_paths']:
        processed_msg['file_paths'] = resolve_media_paths(processed_msg['file_paths'])

    if 'video_paths' in processed_msg and processed_msg['video_paths']:
        processed_msg['video_paths'] = resolve_media_paths(processed_msg['video_paths'])


    # 准备共享的数据
    shared_data = {
        'group_name': group_name,
        'expected_member_count': expected_member_count,
        'test_case': test_case,
        'group_page': group_page,
        'instance_manager': instance_manager,
        'processed_msg': processed_msg,  # 添加处理后的消息
        'member_account':member_account,
        'target_phone':target_phone,
        'select_count':select_count
    }
    print("=== 群聊模块 setup 完成 ===")
    # 执行所有群聊测试用例
    yield shared_data
    # 所有群聊测试结束后执行teardown
    print("=== 开始群聊模块 teardown ===")
    # 解散群聊
    try:
        group_page.dissolve_group(group_name)
        print("群聊解散成功")

    except Exception as e:
        print(f"解散群聊失败: {e}")
    print("=== 群聊模块 teardown 完成 ===")

@pytest.fixture(scope="function")
def shared_group(shared_group_setup_teardown):
    """为每个群聊测试用例提供共享的群聊信息"""
    return shared_group_setup_teardown














































