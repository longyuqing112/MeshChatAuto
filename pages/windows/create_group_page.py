import time

from base.electron_pc_base import ElectronPCBase
from pages.windows.card_message_page import CardMessagePage
from pages.windows.loc.friend_locators import CREATE_MENU_BUTTON, CREATE_MENU_CONTAINER
from selenium.webdriver.support.wait import WebDriverWait

from pages.windows.loc.group_locators import CROUP_CHAT, CROUP_NAME_DIALOG, CROUP_NAME_INPUT, GROUP_DIALOG_CONFIRM, \
    GROUP_FRIENDS_DIALOG, MEMBER_NUMBER, SUCCESS_GROUP_TIP
from pages.windows.loc.message_locators import CONFIRM_SHARE, RIGHT_ITEM_CLOSE
from pages.windows.message_text_page import MessageTextPage

class GroupPage(ElectronPCBase):

    def __init__(self, driver):
        super().__init__()  # 调用父类构造函数
        self.driver = driver  # 设置 driver
        self.wait = WebDriverWait(driver, 10, 0.5)
        self.msg_page = MessageTextPage(driver)  # 复用消息发送功能
        self.card_page = CardMessagePage(self.driver)  # 直接复用已有页面对象

    def create_group(self,message_content,search_queries):
        self.card_page.open_menu_panel('home')
        self.base_click(CREATE_MENU_BUTTON)
        self.base_find_element(CREATE_MENU_CONTAINER)
        self.base_click(CROUP_CHAT)
        self.base_find_element(CROUP_NAME_DIALOG)
        self.base_input_text(CROUP_NAME_INPUT,message_content)
        self.base_click(GROUP_DIALOG_CONFIRM)
        dialog_element = GROUP_FRIENDS_DIALOG
        result = self.card_page.select_friends(search_queries,'list',dialog_element)
        selected_count  = result['selected_count']
        assert selected_count  >= 2, f"创建群组必须选择至少2人，当前选中 {selected_count } 人"
        self.card_page.confirm_share()
        expected_member_count = len(search_queries) + 1
        print("群数量:",expected_member_count)
        self.verify_create_group(message_content,expected_member_count,search_queries)
        return expected_member_count

    def get_current_group_count(self):
        """获取当前群组人数"""
        current_group_number = self.base_get_text(MEMBER_NUMBER)
        return int(current_group_number.strip("()"))  # 去掉括号

    def verify_create_group(self,message_content,expected_member_count,search_queries,inviter_number=None,receiver_member_account=None):
        self.msg_page.open_chat_session('session_list',message_content)
        current_count = self.get_current_group_count()
        assert current_count == expected_member_count, f"预期数量 {expected_member_count},当前数量{current_count}不符合"
        content_tip = self.base_get_text(SUCCESS_GROUP_TIP)
        print('成功得到建群提示: ',content_tip)
        if inviter_number:
          # 接收者端的验证： "19911111111" invited you and "19911113333" to the group chat
            other_members = [m for m in search_queries if m != receiver_member_account and m != inviter_number]
            if len(other_members)== 1:
                expected_tip = f'"{inviter_number}" invited you and "{other_members[0]}" to the group chat'
            else:  # 接收者和多个其他成员被邀请
                other_members_str =','.join(other_members) # 直接连接号码，不要额外的引号
                expected_tip = f'"{inviter_number}" invited you and "{other_members_str}" to the group chat'
        else:
            # 创建者端的验证：You invited "19911114444, 19911113333" to the group chat
            expected_invited_str  = ', '.join(search_queries)
            expected_tip = f'You invited "{expected_invited_str}" to the group chat'
        assert content_tip == expected_tip,f"预期提示: '{expected_tip}', 实际提示: '{content_tip}'"



    def verify_member_receiver(self,instance_manager,member_account,group_name,expected_member_count,search_queries,inviter_number):
        member_driver = instance_manager.start_receiver_instance(member_account)
        member_page = GroupPage(member_driver)
        member_page.msg_page.open_chat_session('session_list',group_name)
        current_count = member_page.get_current_group_count()
        assert current_count == expected_member_count, f"预期数量 {expected_member_count},当前数量{current_count}不符合"
        # content_tip = member_page.base_get_text(SUCCESS_GROUP_TIP)
        # print('成功得到建群提示: ', content_tip)
        # 传递 inviter_number 来验证接收者端的提示消息
        receiver_member_account =member_account['username']
        member_page.verify_create_group(group_name,expected_member_count,search_queries,inviter_number,receiver_member_account)








