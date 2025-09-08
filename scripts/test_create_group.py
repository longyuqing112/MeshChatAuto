import os
import time

import pytest

from pages.windows.create_group_page import GroupPage
from utils.config_utils import ConfigUtils
from utils.dir_utils import resolve_media_paths
from utils.mul_login import MultiInstanceManager
from utils.random_utils import generate_random_id

# current_dir = os.path.dirname(__file__)
# 拼接 YAML 文件的绝对路径
# yaml_file_path = os.path.abspath(os.path.join(current_dir, "../data/group_data.yaml"))

base_dir = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.abspath(os.path.join(base_dir, "../"))


current_dir = os.path.dirname(__file__)
yaml_file_path = os.path.abspath(os.path.join(current_dir, "../data/group_data.yaml"))

def load_test_data(file_path,render_vars=True):
    """
        加载测试数据，支持模板变量渲染
    """
    config_utils = ConfigUtils(file_path)
    data =  config_utils.read_config(render_vars=render_vars)
    return {
        'group_msg_reply': data.get('group_msg_reply', []),
    }

def load_multi_accounts():
    config = ConfigUtils(yaml_file_path).read_config(render_vars=True)
    return  config["create_group"]


# @pytest.mark.parametrize(
#     "test_case",load_test_data(yaml_file_path,render_vars=True)['create_group'],
# )
# def test_create_group(driver,auto_login,test_case):
#     group_page = GroupPage(driver)
#     inviter_number =  test_case['creator_number']
#     test_id = generate_random_id(5)
#     name = test_case['group_name']
#     all_msg = test_case['messages']
#     target_phone = test_case['target_phone']
#     select_count = test_case['select_count']
#     search_queries = test_case['search_queries']
#     group_name = f"{name}[ID:{test_id}]"
#     expected_member_count = group_page.create_group(
#         message_content = group_name,
#         search_queries = search_queries,
#                             )
#     # 1. 初始化多实例管理器
#     instance_manager = MultiInstanceManager(driver)
#     # 1. 初始化多实例管理器
#     accounts =  load_multi_accounts()
#     member_account = next(a for a in accounts)
#     group_page.verify_member_receiver(instance_manager,
#                                       member_account,
#                                       group_name,
#                                       expected_member_count,
#                                       search_queries,
#                                       inviter_number)

def test_send_group_messages(driver, shared_group):
    # 2. 预处理消息配置中的文件路径
    group_page = shared_group['group_page']
    instance_manager = shared_group['instance_manager']
    # test_case = shared_group['test_case']
    processed_msg = shared_group['processed_msg']  # 使用预处理的消息
    group_name = shared_group['group_name']
    # all_msg = test_case['messages']
    member_account = shared_group['member_account']
    target_phone = shared_group['target_phone']
    select_count = shared_group['select_count']
    # processed_msg = all_msg.copy()
    print(f"正在测试发送消息，群聊: {group_name}")
    # # 处理图片路径
    # if 'image_paths' in processed_msg and processed_msg['image_paths']:
    #     processed_msg['image_paths'] = resolve_media_paths(processed_msg['image_paths'])
    #     print(f"处理后的图片路径: {processed_msg['image_paths']}")
    # if 'file_paths' in processed_msg and processed_msg['file_paths']:
    #     processed_msg['file_paths'] = resolve_media_paths(processed_msg['file_paths'])
    #     print(f"处理后的文件路径: {processed_msg['file_paths']}")
    #     # 处理视频路径
    # if 'video_paths' in processed_msg and processed_msg['video_paths']:
    #     processed_msg['video_paths'] = resolve_media_paths(processed_msg['video_paths'])
    #     print(f"处理后的视频路径: {processed_msg['video_paths']}")

    send_results  = group_page.send_all_message(instance_manager,member_account,processed_msg,
                                target_phone=target_phone,
                                group_name=group_name
                                )
    assert all(send_results.values()),f"消息发送失败: {send_results}"
    # 4. 回到原来的群组中并验证接收端
    group_page.msg_page.open_chat_session('session_list', group_name)
    #验证所有消息
    success = group_page.verify_all_messages_receiver(group_name,select_count,processed_msg,target_phone)
    assert success, "消息验证失败"


@pytest.mark.parametrize(
    "test_case",load_test_data(yaml_file_path,render_vars=True)['group_msg_reply'],
)
def test_group_msg_action(driver,shared_group,test_case):
    """测试群消息引用功能"""
    group_page = shared_group['group_page']
    instance_manager = shared_group['instance_manager']
    group_name = shared_group['group_name']
    member_account = shared_group['member_account']
    group_page.msg_page.open_chat_session('session_list', group_name)
    if isinstance(test_case['original_messages'][0], str):
        msg_type = 'text'
        group_page.msg_page.send_multiple_message(test_case.get('original_messages'))
        print('获取引用的内容：', test_case.get('original_messages'))
    else:
        media_data = test_case['original_messages'][0]
        msg_type = media_data['type']
        file_path = os.path.abspath(os.path.join(src_dir, media_data['path']))
        group_page.msg_page.send_media_messages(
            file_paths=[file_path],
            media_type=msg_type
        )
    member_driver = instance_manager.start_receiver_instance(member_account)
    member_page = GroupPage(member_driver)
    expected_contains_original = test_case['expected'].get('contains_original', True)
    cancel_quote = test_case.get('cancel_quote', False, )
    member_page.msg_page.open_chat_session('session_list', group_name)
    latest_element = member_page.action_page._get_latest_message_element()
    # 2. 执行回复操作
    assert group_page.action_page.reply_to_message(
        test_case['reply_text'],
        cancel_quote=cancel_quote,
        expected_contains_original=expected_contains_original,
        original_type = msg_type  # 新增参数
    ), "回复操作失败"
    print("切换到接收端验证消息...")
    time.sleep(3)
    member_page.msg_page.open_chat_session('session_list', group_name)


    # 实际ui->context_element--是引用中的新消息 预期-> reply_text--是原始消息
    context_element = member_page._get_context_element(latest_element, msg_type)
    member_page.action_page._verify_reply_content( test_case['reply_text'], context_element, expected_contains_original,
                                                          msg_type)












