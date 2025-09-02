import os
import time

from selenium.webdriver.common.by import By

from base.electron_pc_base import ElectronPCBase
from pages.windows.card_message_page import CardMessagePage
from pages.windows.loc.friend_locators import CREATE_MENU_BUTTON, CREATE_MENU_CONTAINER
from selenium.webdriver.support.wait import WebDriverWait

from pages.windows.loc.group_locators import CROUP_CHAT, CROUP_NAME_DIALOG, CROUP_NAME_INPUT, GROUP_DIALOG_CONFIRM, \
    GROUP_FRIENDS_DIALOG, MEMBER_NUMBER, SUCCESS_GROUP_TIP
from pages.windows.loc.message_locators import CONFIRM_SHARE, RIGHT_ITEM_CLOSE
from pages.windows.message_text_page import MessageTextPage
from pages.windows.msg_actions_page import MsgActionsPage


class GroupPage(ElectronPCBase):

    def __init__(self, driver):
        super().__init__()  # 调用父类构造函数
        self.driver = driver  # 设置 driver
        self.wait = WebDriverWait(driver, 10, 0.5)
        self.msg_page = MessageTextPage(driver)  # 复用消息发送功能
        self.card_page = CardMessagePage(self.driver)  # 直接复用已有页面对象
        self.action_page = MsgActionsPage(driver)

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


    def send_all_message(self,instance_manager,member_account,all_msg,target_phone,group_name=None):
        member_driver = instance_manager.start_receiver_instance(member_account)
        member_page = GroupPage(member_driver)
        print(f"接收到消息参数：{all_msg}")
        results = {}
        #发送除了名片消息的 其他消息
        message_results = member_page.msg_page.send_group_messages(all_msg)
        results.update(message_results)
        # 单独发送名片消息
        if target_phone:
            print(f"开始发送: {target_phone}名片给群组: {group_name}")
            member_page.card_page.preare_share_friends(target_phone)
            member_page.card_page.select_friends(
                    [group_name],
                    'list'
                )
            member_page.card_page.confirm_share()
            results['card'] = True
            print("名片消息发送成功")
        return results  # 必须返回结果！

    def verify_all_messages_receiver(self,group_name,expected_count,expected_messages,target_phone=None):
        self.msg_page.open_chat_session('session_list',group_name)
        # 等待聊天窗口加载完成
        import time
        time.sleep(2)
        actual_messages_element = self.action_page.get_group_n_message(expected_count)
        print(f"获取到 {len(actual_messages_element)} 条最新消息")
        if len(actual_messages_element) < expected_count:
            print(f"警告: 只找到 {len(actual_messages_element)} 条消息，预期 {expected_count} 条")
            return False
        # 2. 分别验证各种消息类型
        verification_results = {
            'text': self._verify_text_messages(actual_messages_element,expected_messages.get('text_messages',[])),
            'image': self._verify_media_messages(actual_messages_element,'image',expected_messages.get('image_paths',[])),
            'file': self._verify_media_messages(actual_messages_element,'file',expected_messages.get('file_paths',[])),
            'video': self._verify_media_messages(actual_messages_element,'video',expected_messages.get('video_paths',[])),
            'card': self._verify_card_messages(actual_messages_element,target_phone)
        }
        # 3. 输出详细结果
        all_passed = all(verification_results.values())
        print(f"消息验证结果: {verification_results}")
        if not all_passed:
            print("部分消息验证失败")
            return False
        print("所有消息验证成功!")
        return True

    def _verify_text_messages(self,actual_messages_element,expected_texts):
        if not expected_texts:
            print('没有文本消息需要验证')
            return True
        print(f"得到实际元素: {actual_messages_element}--预期元素：{expected_texts}")
        found_texts = []
        # for msg in actual_messages_element:
        for i, msg_container in enumerate(actual_messages_element):
            try:
                # 打印消息容器的HTML结构用于调试
                container_html = msg_container.get_attribute('outerHTML')
                print(f"消息容器 {i} 的HTML: {container_html[:500000]}...")  # 只打印前200字符
                # 查找文本消息元素
                texts_elements = msg_container.find_elements(By.CSS_SELECTOR, ".whitespace-pre-wrap")
                print(f'获取到 {len(texts_elements)} 个文本元素')
                print('获取到其中的文本elements：', texts_elements)
                for element in texts_elements:
                    text = element.text.strip()
                    print(f"检查文本: '{text}'")
                    if text in expected_texts and text not in found_texts:#去重
                        found_texts.append(text)
                        print(f"找到文本消息: {text}")
            except:
                continue
        result = set(expected_texts) == set(found_texts)
        print(f"文本消息验证: 预期{expected_texts}, 找到{found_texts}, 结果{result}")
        return result

    def _verify_media_messages(self,actual_messages_element,media_type,expected_texts):
        """验证媒体消息（图片、视频、文件）"""
        if not expected_texts:
            print("没有图片消息需要验证")
            return True
        expected_count = len(expected_texts)  # 图片文件的数量
        expected_files = []

        for path in expected_texts:
            try:
                filename = os.path.basename(path)
                # 去掉扩展名，只保留基本名称用于匹配
                base_name = os.path.splitext(filename)[0]
                expected_files.append(base_name)
                print(f"预期{media_type}文件: {base_name}")
            except Exception as e:
                print(f"处理文件路径时出错: {e}")
                continue

        found_files = []
        for msg in actual_messages_element:
            try:
                if media_type == 'image':
                    # 查找图片消息元素
                    media_elements = msg.find_elements(By.TAG_NAME, 'img')
                    for element in media_elements:
                        src = element.get_attribute('src') or ''
                        for expected_file in expected_files:
                            if expected_file in src and expected_file not in found_files:
                                found_files.append(expected_file)
                                print(f"找到图片消息: {expected_file}, src: {src}")

                elif media_type == 'video':
                    # 查找视频消息元素

                    video_elems = msg.find_elements(By.CSS_SELECTOR, 'div.video.cursor-pointer')
                    print(f"找到 {len(video_elems)} 个视频元素")
                    for container in video_elems:
                        # 在视频容器中查找img标签
                        img_elements = container.find_elements(By.TAG_NAME, 'img')

                        for img in img_elements:
                            # print(f"视频元素 {idx}: ", element.get_attribute('outerHTML'))
                            src = img.get_attribute('src') or ''
                            alt  = img.get_attribute('alt') or ''
                            print(f"视频缩略图 - src: {src}, alt: {alt}")
                            for expected_file in expected_files:
                                if expected_file in src and expected_file not in found_files:
                                    found_files.append(expected_file)
                                    print(f"找到视频消息: {expected_file}")

                elif media_type == 'file':
                    # 查找文件消息元素
                    media_elements = msg.find_elements(By.CSS_SELECTOR, ".file-message, [class*='file']")
                    for element in media_elements:
                        file_text = element.text.lower()
                        for expected_file in expected_files:
                            if expected_file.lower() in file_text and expected_file not in found_files:
                                found_files.append(expected_file)
                                print(f"找到文件消息: {expected_file}, 文本: {file_text}")

            except Exception as e:
                print(f"验证{media_type}消息时出错: {e}")
                continue

        result = set(expected_files) == set(found_files)
        print(f"{media_type}消息验证: 预期{expected_files}, 找到{found_files}, 结果{result}")
        return result

    def _verify_card_messages(self, actual_messages_element, target_phone):
        """验证名片消息"""
        if not target_phone:
            print("没有名片消息需要验证")
            return True

        for message in actual_messages_element:
            try:
                # 查找名片消息元素
                card_elements = message.find_elements(By.CSS_SELECTOR, ".card")
                if card_elements:
                    # 进一步验证名片内容
                    card_text = card_elements[0].text
                    if target_phone in card_text:
                        print(f"找到名片消息: 包含 {target_phone}")
                        return True
                    else:
                        print(f"找到名片但号码不匹配: {card_text}")
            except:
                continue

        print("未找到名片消息")
        return False












