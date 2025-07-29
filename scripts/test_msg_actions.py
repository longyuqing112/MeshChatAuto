import os
import pytest

from pages.windows.card_message_page import CardMessagePage
from pages.windows.message_text_page import MessageTextPage
from pages.windows.msg_actions_page import MsgActionsPage
from utils.config_yaml_utils import YamlConfigUtils

current_dir = os.path.dirname(__file__)
# 拼接 YAML 文件的绝对路径
yaml_file_path = os.path.abspath(os.path.join(current_dir, "../data/message_data.yaml"))

base_dir = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.abspath(os.path.join(base_dir, "../"))


def load_test_data(file_path):
    yaml_utils = YamlConfigUtils(file_path)
    data = yaml_utils.load_yaml_test_data()
    return {
        'reply_tests': data.get('reply_tests', []),
        'forward_message_tests': data.get('forward_message_tests', []),
        'select_message_tests': data.get('select_message_tests', []),
        'delete_message_tests': data.get('delete_message_tests', []),
        'recall_message_tests': data.get('recall_message_tests', []),
        'edit_message_tests': data.get('edit_message_tests', []),
        'copy_message_tests': data.get('copy_message_tests', [])
    }

@pytest.mark.parametrize(
    "test_case",
    load_test_data(yaml_file_path)['reply_tests'],
    ids=lambda case: case["name"]
)
def test_msg_reply(driver,test_case,auto_login):
    # 初始化页面对象
    msg_page = MessageTextPage(driver)
    action_page = MsgActionsPage(driver)
    msg_page.open_chat_session(target=test_case['target'], phone=test_case['target_phone'],)
    # 获取消息类型
    # msg_type = test_case.get('original_messages')
    msg_type = test_case['original_messages']
    # 1. 先发送原始消息
    if isinstance(test_case['original_messages'][0], str):
        msg_type = 'text'
        msg_page.send_multiple_message(test_case.get('original_messages'))
        print('获取引用的内容：', test_case.get('original_messages'))
    else:# 媒体消息
        media_data = test_case['original_messages'][0]
        msg_type = media_data['type']
        #————————————meshchat没有语音消息——————————
        # if msg_type == 'voice':
        #     msg_page.send_voice_message(record_seconds=media_data['duration'])
        # else:
        # ————————————meshchat没有语音消息——————————
        # 修正文件路径为绝对路径
        file_path = os.path.abspath(os.path.join(src_dir, media_data['path']))
        msg_page.send_media_messages(
            file_paths=[file_path],
            media_type=msg_type
        )
    expected_contains_original = test_case['expected'].get('contains_original', True)
    cancel_quote = test_case.get('cancel_quote', False,)

    # 2. 执行回复操作
    assert action_page.reply_to_message(
        test_case['reply_text'],
        cancel_quote=cancel_quote,
        expected_contains_original=expected_contains_original,
        original_type = msg_type  # 新增参数
    ),"回复操作失败"

@pytest.mark.parametrize(
    "test_case",load_test_data(yaml_file_path)['forward_message_tests'],
)
def test_forward_friends(driver,test_case):
    msg_page    = MessageTextPage(driver)
    msg_page.open_chat_session(target=test_case['target'], phone=test_case['target_chat'], )
    msg_type = test_case.get('message_content')
    media_type = None  # 👈 默认无媒体类型

    if test_case.get('media_type') == 'emoji':
        msg_page.send_emoji_message(
            emoji_names=test_case['message_content'],
            send_method='click'
        )
        media_type = 'emoji'
        message_content = test_case['message_content']
    else:
        if isinstance(test_case['message_content'][0], str):
            msg_type = 'text'
            msg_page.send_multiple_message(test_case['message_content'])
        else: #媒体类型不包括语音消息 因为语音不能转发
            media_data = test_case['message_content'][0]
            file_path = os.path.abspath(os.path.join(src_dir, media_data['path']))
            media_type = test_case.get('media_type')  # 👈 安全获取，默认图片类型
            # 验证文件存在性
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            msg_page.send_media_messages([file_path], media_type)
    #执行转发操作
    action_page = MsgActionsPage(driver)
    result = action_page.forward_to_message(
        message_content=test_case['message_content'],
        search_queries=test_case['search_queries'],
        select_type=test_case.get('select_type', 'search'),  # 使用默认值
        operation_type=test_case['operation_type'],
        media_type= media_type
    )
    # 清除操作的验证
    if test_case.get('operation_type') == 'clear':
        # 初始数量断言
        assert result['initial_count'] == test_case['expected']['initial_selected']

        # 清除操作和最终状态验证已在 forward_to_message 中完成

@pytest.mark.parametrize(
    "test_case",load_test_data(yaml_file_path)['select_message_tests'],
)
def test_select_forward(driver,test_case):
    msg_page = MessageTextPage(driver)
    msg_page.open_chat_session(target=test_case['target'], phone=test_case['target_chat'])
    msg_page.send_multiple_message(test_case['message_content'])
    # 执行选择-转发操作
    action_page = MsgActionsPage(driver)
    action_page.select_and_forward_message(
        search_queries= test_case['search_queries'],
        select_type=test_case["select_type"],
        operation_type = test_case["operation_type"],
        expected_content = test_case["message_content"],
        select_count = test_case["select_count"]
    )

@pytest.mark.parametrize(
    "test_case",load_test_data(yaml_file_path)['delete_message_tests'],
)
def test_delete_msg(driver,test_case):
    msg_page = MessageTextPage(driver)
    msg_page.open_chat_session(target=test_case['target'], phone=test_case['target_chat'])
    msg_page.send_multiple_message(test_case['message_content'])
    # 执行选择-删除操作
    action_page = MsgActionsPage(driver)
    action_page.delete_to_message(
        expected_content=test_case["message_content"],
        operation_type = test_case["operation_type"]
    )

@pytest.mark.parametrize(
    "test_case",load_test_data(yaml_file_path)['recall_message_tests'],
)
def test_recall_msg(driver,test_case):
    msg_page = MessageTextPage(driver)
    card_page = CardMessagePage(driver)
    msg_page.open_chat_session(target=test_case['target'], phone=test_case['target_chat'])
    if test_case.get('media_type') == 'emoji':
        msg_page.send_emoji_message(
            emoji_names=test_case['message_content'],
            send_method='click'
        )
    elif test_case.get('media_type') == 'text':
        msg_page.send_multiple_message(test_case['message_content'])
        #————————————————————没有语音消息
    # elif test_case.get('media_type') == 'voice':
    #     msg_page.send_voice_message(test_case['message_content'][0]['duration'])
    elif test_case.get('media_type') == 'card':
        card_page.preare_share_friends(phone=test_case['target_chat'])
        card_page.select_friends( search_queries=test_case['message_content'], select_type="list")
        card_page.confirm_share()
        card_page.open_menu_panel("home")
        msg_page.open_chat_session(target=test_case['target'], phone=test_case['message_content'][0])

    else:
        media_data  = test_case['message_content'][0]
        file_path = os.path.abspath(os.path.join(src_dir, media_data['path']))
        media_type = test_case.get('media_type')
        # 验证文件存在性
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        msg_page.send_media_messages([file_path], media_type=media_type)
    # 执行选择-撤回操作
    action_page = MsgActionsPage(driver)
    action_page.recall_to_message (
        media_type = test_case["media_type"]
    )

#———————————————meshchat没有消息编辑————————————

# @pytest.mark.parametrize(
#     "test_case", load_test_data(yaml_file_path)['edit_message_tests'],
# )
# def test_edit_msg(driver, test_case):
#     msg_page = MessageTextPage(driver)
#     msg_page.open_chat_session(target=test_case['target'], phone=test_case['target_chat'])
#     msg_page.send_multiple_message(test_case['message_content'])
#     # 执行编辑操作
#     action_page = MsgActionsPage(driver)
#     action_page.edit_to_msg(
#         new_content = test_case["new_content"],
#         operation_type = test_case.get("operation_type", "confirm"),  # 设置默认值
#     )
#———————————————meshchat没有消息编辑————————————

@pytest.mark.parametrize(
    "test_case", load_test_data(yaml_file_path)['copy_message_tests'],
)
def test_copy_msg(driver, test_case):
    msg_page = MessageTextPage(driver)
    msg_page.open_chat_session(target=test_case['target'], phone=test_case['target_chat'])
    media_data = test_case['message_content']
    media_type = test_case.get('media_type')
    # 仅在需要媒体路径时构建路径
    file_paths = [os.path.abspath(os.path.join(src_dir, m['path'])) for m in media_data] if isinstance(media_data[0], dict) else None
    # file_paths = [file_path]  # 直接使用单个文件路径的列表
    if media_type == 'text':
        msg_page.send_multiple_message(test_case['message_content'])
    elif test_case.get('media_type') == 'emoji':
        msg_page.send_emoji_message(
            emoji_names=test_case['message_content'],
            send_method='click'
        )
    else:
        print('fil',file_paths[0])
        if not os.path.exists(file_paths[0]):
            raise FileNotFoundError(f"文件不存在: {file_paths[0]}")
        msg_page.send_media_messages(file_paths, media_type=media_type)
    # 执行f复制操作
    action_page = MsgActionsPage(driver)
    action_page.copy_to_message(
        operations=test_case['operations'],
        message_content=media_data,
        media_type = media_type,
        file_paths = file_paths
    )












