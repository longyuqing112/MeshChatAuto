from pages.windows.card_message_page import CardMessagePage
import os
import pytest

from pages.windows.loc.message_locators import CONFIRM_SHARE, RIGHT_ITEM, CANCEL_SHARE
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
        'share_card_tests': data.get('share_card_tests', []),
    }

@pytest.mark.parametrize(
    "test_case",load_test_data(yaml_file_path)['share_card_tests'],
    ids = lambda case:case["name"]  # 使用测试用例的名称作为标识
)
def test_share_search_friend(driver,test_case):
    share_search_friend_page = CardMessagePage(driver)
    share_search_friend_page.preare_share_friends(phone=test_case['target_phone'])
    result = share_search_friend_page.select_friends(
        search_queries=test_case['search_queries'],
        select_type = test_case['select_type']
    )
    # 根据操作类型分流
    if test_case.get('operation_type') == 'clear':
        # 验证初始数量
        assert result['selected_count'] == test_case['expected']['initial_selected']
        # 执行清除操作
        share_search_friend_page.clear_all_selected_friends()
        # 验证最终状态
        share_search_friend_page._verify_final_state()

    elif test_case.get('operation_type') == 'cancel':
        # 记录分享前的时间点
        cancel_time = share_search_friend_page.cancel_share()
        # 验证会话未更新
        share_search_friend_page.verify_no_share_content(
            expected_names=result['expected_names'],
            unexpected_content=result['card_content'],
            initial_time=cancel_time
        )
    else: # 原有分享验证逻辑
        assert result['selected_count'] == len(test_case['search_queries']), f"已选数量 {result['selected_count']} 与预期 {len(search_queries)} 不一致" \
        # 确认发送分享按钮 and 获取分享后的时间
        share_time = share_search_friend_page.confirm_share()
        share_search_friend_page.verify_share_content(
            expected_names=result['expected_names'],
            expected_content=result['card_content'],
            expected_time=share_time
        ) 
