import os
import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from pages.windows.loc.message_locators import TEXTAREA_INPUT
from pages.windows.login_securenet_page import LoginPage
from pages.windows.message_text_page import MessageTextPage
from  selenium.webdriver.support import  expected_conditions as EC

from utils.config_yaml_utils import YamlConfigUtils

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
        'message_tests': data.get('message_tests', []),
        'operation_tests': data.get('operation_tests', []),
        'media_tests': data.get('media_tests', []),
        'emoji_tests': data.get('emoji_tests', [])
    }

@pytest.fixture(scope="module")
def shared_message_window(driver):
    """仅在需要消息窗口的测试用例中使用此 fixture"""
    page = MessageTextPage(driver)
    current_phone = page.get_current_phone_number()
    print('当前手机号码是：',current_phone)
    page.open_avatar_menu()
    page.verify_message_window_phone(current_phone)
    yield  page


# 普通消息测试
@pytest.mark.parametrize(
    "test_case",load_test_data(yaml_file_path)['message_tests'],
    ids = lambda case:case["name"]  # 使用测试用例的名称作为标识
)
def test_multiple_messages(shared_message_window,test_case,auto_login):
    if 'target_phone' in test_case:
        result = shared_message_window.all_send_message(
            messages=test_case['messages'],
            target=test_case['target'],
            phone=test_case['target_phone'],
            send_method=test_case['send_method'],
            timeout=10
        )
    else:# 发消息给自己
        # message_text_page = MessageTextPage(driver)
        result = shared_message_window.send_multiple_message(
            messages=test_case["messages"],
            send_method=test_case["send_method"],
            timeout=10)
        assert result,f"测试失败 | 用例: {test_case['name']} | 方法: {test_case['send_method']} | 消息: {test_case['messages']}"


# 操作流程测试
@pytest.mark.parametrize(
    "test_case",
    load_test_data(yaml_file_path)['operation_tests'],
    ids=lambda case: case["name"]
)
def test_operations(shared_message_window, test_case,auto_login):
    # 清空输入框
    shared_message_window.enter_message("")

    # 输入初始文本
    shared_message_window.enter_message(test_case['messages'][0])
    time.sleep(0.5)

    # 执行操作序列
    for operation in test_case["operations"]:
        shared_message_window.perform_operation(action_type=operation)
        time.sleep(0.5)

    # 验证结果
    element = shared_message_window.base_find_element(TEXTAREA_INPUT)
    current_text = element.text or element.get_attribute('value')

    assert test_case['messages'][
               0] == current_text, f"操作后内容不符，预期: {test_case['messages'][0]}，实际: {current_text}"

    # 发送验证（如果需要）
    if "send_method" in test_case:
        if test_case["send_method"] == 'click':
            shared_message_window.send_message()
        elif test_case["send_method"] == 'enter':
            shared_message_window.send_message_via_enter()
        if 'cut' not in test_case["messages"]:# 剪切操作不验证消息发送
            assert shared_message_window.is_text_message_in_chat(test_case['messages'][0]), "消息发送验证失败"

#发送媒体类型
@pytest.mark.parametrize(
    "test_case",
    load_test_data(yaml_file_path)['media_tests'],
    ids=lambda case: case["name"]
)
def test_media_messages(shared_message_window,test_case,auto_login):
    #处理动态路径
    print("路径src_dir:",src_dir)
    file_paths = [
    os.path.normpath(os.path.join(src_dir, p.replace("/",os.sep)))
    for p in test_case["file_path"]
    ]
    print("最终文件路径列表：", file_paths)
    target = test_case.get('target', 'me')
    phone = test_case.get('target_phone')
    media_type=test_case.get('expected_type')

    #执行发送
    result = shared_message_window.send_media_messages(
        file_paths=file_paths,
        media_type=media_type,
        target=target,
        phone=phone,
        timeout=20
    )
    # 验证逻辑
    assert result, f"媒体消息发送失败 | 用例: {test_case['name']}"
    if target=='friend':
        assert shared_message_window.verify_message_window_phone(
            test_case['target_phone']
        ), "接收方验证失败"

@pytest.mark.parametrize(
    "test_case",
    load_test_data(yaml_file_path)['emoji_tests'],
    ids=lambda case: case["name"])
def test_emoji_message(shared_message_window,test_case,auto_login):
    target = test_case.get('target', 'friend')
    phone = test_case.get('target_phone')
    shared_message_window.open_chat_session(target=target, phone=phone)
    # 发送表情
    send_success = shared_message_window.send_emoji_message(
        emoji_names=test_case['emoji_names'],
        send_method=test_case['send_method']
    )
    assert send_success, "表情消息发送失败"
    # 验证消息
    assert shared_message_window.verify_emoji_message(test_case['expected']['sequence']), \
        "表情消息验证失败"


    #————————————————————meshchat没有语音消息————————————————————————

# @pytest.mark.parametrize("test_data", [
#     {"duration": 3, "expected": 3}], ids=["短语音消息"])
# def test_voice_message(shared_message_window, test_data):
#     shared_message_window.open_chat_session(target="friend", phone="18378056217")
#     assert shared_message_window.send_voice_message(record_seconds=test_data['duration']),"录音操作失败"
#     # 复合验证
#     is_success, actual = shared_message_window.verify_voice_message(
#         expected_duration=test_data["expected"]
#     )
#     # 断言结果
#     assert is_success, f"验证失败 | 预期: {test_data['expected']}s 实际: {actual}s"
#
