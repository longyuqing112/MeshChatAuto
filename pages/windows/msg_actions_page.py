import os
import time
import re
from datetime import timedelta, datetime
from pyexpat.errors import messages
from selenium.webdriver.common.by import By
from unicodedata import category

from base.electron_pc_base import ElectronPCBase
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from  selenium.webdriver.support import  expected_conditions as EC
from selenium.webdriver import Keys, ActionChains
from selenium.common import NoSuchElementException

from pages.windows.card_message_page import CardMessagePage
from pages.windows.loc.message_locators import MSG_ACTIONS_FORWARD, \
    CHAT_QUOTE_MSG_CITE, QUOTE_BOX_CLOSE, QUOTE_BOX, CHAT_QUOTE_MSG2_BE_CITE_TXT, CHAT_QUOTE_IMG_TH, \
    CHAT_FILE_NAME, FILE_NAME, \
    CHAT_QUOTE_IMG_MP4, RIGHT_ITEM, CONFIRM_SHARE, SESSION_ITEMS, SESSION_ITEM_UPDATES, SESSION_ITEM_UPDATES_TIME, \
    MSG_READ_STATUS, CANCEL_SHARE, SELECT_FORWARD, CHECK_ELEMENT, SELECT_DELETE, \
    CONFIRM_SELECT_DELETE, SELECT_CLOSE, MSG_ACTIONS_DELETE, MSG_ACTIONS_RECALL, MSG_ACTIONS_EDIT, EDIT_TIP, \
    MSG_ACTIONS_COPY, MSG_ACTIONS_QUOTE, MSG_ACTIONS_MULTIPLE, MSG_ACTIONS_FAVORITE, FAVORITE_RIGHT_LIST, FAVORITE_ITEM, \
    FAVORITE_ITEM_TIME, FAVORITE_ITEM_CONTENT, FAVORITE_ITEM_NAME, ALL_FAVORITES, VIEW_CONTENT_NAME, VIEW_CONTENT_IMAGE, \
    VIEW_CONTENT_VIDEO, VIEW_CONTENT_FILE, TEXT_CONTENT, INDEX_ROW, MENU_FAVORITE, TIP_SUCCESS, CHECKBOX, \
    SELECT_FAVORITE, CONTENT_TIME, SHARE_FRIENDS_DIALOG
from pages.windows.loc.settings_locators import DIALOG_CONTAINER
from pages.windows.message_text_page import MessageTextPage


class MessageStatus:
    SENT = "read-none"  # 已发送，对方不在线，对方还没接收
    READ = "read-over"  # 已读
    FAILED = "failed"  # 可选：发送失败状态
    ARRIVED = "read-arrived"  #对方在线，已经收到了但未读


class MsgActionsPage(ElectronPCBase):

    def __init__(self, driver):
        super().__init__()  # 调用父类构造函数
        self.driver = driver  # 设置 driver
        self.wait = WebDriverWait(driver, 10, 0.5)
        self.msg_page = MessageTextPage(driver)  # 复用消息发送功能
        self.card_page = CardMessagePage(self.driver)  # 直接复用已有页面对象



    def cancel_quote(self):
        """取消引用"""
        self.base_click(QUOTE_BOX_CLOSE)
        WebDriverWait(self.driver, 5).until(
            EC.invisibility_of_element_located(QUOTE_BOX)
        )
    def _select_context_menu(self,action):
        menu_item={
            'Quote': MSG_ACTIONS_QUOTE,
            'Forward': MSG_ACTIONS_FORWARD,
            'Multiple': MSG_ACTIONS_MULTIPLE,
            'Delete': MSG_ACTIONS_DELETE,
            'Recall': MSG_ACTIONS_RECALL,
            'Edit': MSG_ACTIONS_EDIT,
            'Copy': MSG_ACTIONS_COPY,
            'Favorite': MSG_ACTIONS_FAVORITE,
        }.get(action)
        time.sleep(1)
        self.base_click(menu_item)

    def _verify_reply_content(self,reply_text,original_text,expected_contains_original,original_type='text'):
        """
               验证回复内容是否包含：
               1. 正确显示被引用消息
               2. 新消息内容正确
               """
        print('打印出',original_text.text)
        print('打印出出传过来的类型', original_type)
        # 获取最新消息（回复消息）
        if expected_contains_original:
            reply_msg = self.msg_page.wait_for_latest_message_in_chat(except_type='quote')
            print('获取引用得消息',reply_msg)
        else:
            reply_msg = self.msg_page.wait_for_latest_message_in_chat(except_type='text')
        actual_reply = ''  # 初始化 actual_reply 变量
        # 验证回复文本
        if expected_contains_original:
            # 验证被引用部分  ------------------
            if original_type == 'text':
                # 验证被引用部分
                quoted_txt = reply_msg['latest_message_element'].find_element(*CHAT_QUOTE_MSG2_BE_CITE_TXT)
                print('验证引用部分', original_text.text)
                print('验证引用部分2', quoted_txt.text)
                # 文本验证
                quoted_text = quoted_txt.text
                assert original_text.text in quoted_text, f"文本引用不匹配: {quoted_text}"

            elif original_type == 'image':
                # 图片验证
                img = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located(CHAT_QUOTE_IMG_TH)
                )
                assert img.is_displayed(), "图片缩略图未显示"
                # 可选：验证缩略图尺寸
                width = img.size['width']
                assert width >= 50, "缩略图宽度不足"

            elif original_type == 'file':
                # 文件验证
                displayed_name = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located(CHAT_FILE_NAME)
                ).text
                print('文件：',displayed_name)
                # 获取原始文件名
                original_file = original_text.find_element(*FILE_NAME)
                expected_name = original_file.text.strip()
                assert expected_name in displayed_name, f"文件名不匹配: {expected_name} vs {displayed_name}"

            elif original_type == 'video':
                # 视频验证
                video_thumb = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located(CHAT_QUOTE_IMG_MP4)
                )
                assert video_thumb.is_displayed(), "视频缩略图未显示"
                # # 可选：验证播放按钮
                # assert self.is_element_present((By.CSS_SELECTOR, ".play-icon")), "播放按钮缺失"

            # elif original_type == 'voice':
            #     # 语音验证
            #     duration = WebDriverWait(self.driver, 5).until(
            #         EC.visibility_of_element_located(CHAT_QUOTE_VOICE)
            #     ).text
            #     assert duration.endswith("s"), "时长格式错误"
            #     # 验证数值范围
            #     duration_seconds = int(duration.strip('s'))
            #     assert 1 <= duration_seconds <= 60, "语音时长超出合理范围" #------------------

            # 统一验证回复文本
            actual_reply = reply_msg['latest_message_element'].find_element(*CHAT_QUOTE_MSG_CITE).text
            assert reply_text  in actual_reply, f"回复文本不匹配：预期包含 '{reply_text}'，实际 '{actual_reply}'"
            # 验证回复文本
            quoted_cite = reply_msg['latest_message_element'].find_element(*CHAT_QUOTE_MSG_CITE)
            print('检测quoted_cite',quoted_cite.text)
            # 根据原始消息类型进行验证 媒体类型也是
            assert reply_text in quoted_cite.text, "回复文本内容不匹配"
        else:
            # 检查是否为普通消息
            quoted_cite_txt = reply_msg['text']
            print('普通消息：', quoted_cite_txt)
            assert reply_text in quoted_cite_txt, f"回复文本不匹配: 期望包含 '{reply_text}', 实际得到 '{quoted_cite_txt}'"
            # 确保无引用框
            assert not self.is_element_present(QUOTE_BOX), "回复仍包含引用框"
        return True

    def is_element_present(self, locator):
        try:
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(locator))
            return True
        except TimeoutException:
            return False


    def _get_latest_message_element(self):
        """获取最新消息元素（带index属性）"""
        latest_index = self.msg_page.latest_msg_index_in_chat()
        print('最新位置：', latest_index)
        return self.wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, f".chat-message div[index='{latest_index}'] .chat-item-content")
            )
        )

    def reply_to_message(self, reply_text, cancel_quote=False, expected_contains_original=True, original_type='text'):

        """右键点击消息并选择回复"""
        latest_element = self._get_latest_message_element()
        context_element = None
        context_element = self._get_context_element(latest_element, original_type)

        # 右键操作
        ActionChains(self.driver).context_click(context_element).perform()
        self._select_context_menu("Quote")
        # latest_msg = latest_element.find_element(By.CSS_SELECTOR,'.whitespace-pre-wrap')
        print('最新消息元素：', context_element)
        # 3. 输入回复内容并发送
        self.msg_page.enter_message(reply_text)
        if cancel_quote:
            self.cancel_quote()
        self.msg_page.send_message()
        # 4. 验证回复内容
        return self._verify_reply_content(reply_text, context_element, expected_contains_original, original_type)

    def forward_to_message(self,message_content,search_queries,select_type="search",operation_type='confirm',media_type=None):
        """触发转发并复用名片分享逻辑"""
        # 1. 定位消息并打开转发菜单
        latest_element = self._get_latest_message_element()
        context_element = self._get_context_element(latest_element, media_type if media_type else 'text')
        ActionChains(self.driver).context_click(context_element).perform()
        self._select_context_menu("Forward")
        # 2. 复用名片分享的选择好友流程

        result = self.card_page.select_friends(search_queries=search_queries,select_type=select_type)
        #由于文本和媒体需是列表形势需要的是[0]但是表情不需要 所以做个声明
        processed_content = message_content[0] if media_type != "emoji" and isinstance(message_content,list) else message_content
        # 3. 根据操作类型处理
        if operation_type == "confirm":
            share_time = self.card_page.confirm_share()
            self._verify_forward_result(
                expected_names=result['expected_names'],
                expected_content=processed_content,  # 使用处理后的内容
                expected_time=share_time,
                media_type=media_type
            )
        elif operation_type == "clear":
            # 记录初始数量
            initial_count = result['selected_count']
            # 执行清空
            self.card_page.clear_all_selected_friends()
            self.card_page._verify_final_state()
            # self.base_click(CANCEL_SHARE)
            return {
                'initial_count': initial_count
            }
        else: #cancel逻辑
            cancel_time = self.card_page.cancel_share()
            self._verify_no_forward(
                expected_names=result['expected_names'],
                unexpected_content=processed_content,  # 使用处理后的内容
                initial_time=cancel_time
            )
    def _verify_forward_result(self,expected_names,expected_content,expected_time,media_type):
        if media_type:
            # 媒体类型专用验证
            self._verify_media_forward(expected_names, expected_content, media_type, expected_time)
        else: #验证文本
            """验证转发结果（复用部分验证逻辑）"""
            self.card_page.verify_share_content(
                expected_names=expected_names,
                expected_content=expected_content,  # 这里传入消息内容而非名片内容
                expected_time=expected_time
            )
    def _verify_no_forward(self,expected_names,unexpected_content,initial_time):
        self.card_page.verify_no_share_content(
            expected_names =expected_names,
            unexpected_content = unexpected_content,
            initial_time = initial_time
        )

    def _verify_media_forward(self,expected_names, expected_content, media_type, expected_time):
        for name in expected_names:#遍历所勾选的
            try:
                session_item = self.card_page.find_and_click_target_card(
                    card_container_loc=SESSION_ITEMS,
                    username_loc=(By.XPATH, f".//div[contains(text(), '{name}')]"),
                    userid_loc=(By.XPATH, f".//div[contains(text(), '{name}')]"),
                    target_phone=name,
                    context_element=None
                )
            # 获取实际显示内容
                actual_content = session_item.find_element(*SESSION_ITEM_UPDATES).text
                print('实际内容',actual_content)
            # 根据类型匹配预期模式
                if media_type == "emoji":
                    self._verify_forwarded_emojis(name, expected_content)
                else:
                    # # 处理文件/视频类型（expected_content是带path的字典列表）
                    # file_data = expected_content[0]  # 获取第一个文件数据
                    # file_path = file_data['path']  # 提取路径字段
                    # file_name = os.path.basename(file_path)
                    if media_type == "image":
                        assert '[Image]' in actual_content,f"未找到图片标识: {actual_content}"
                    elif media_type == "video":
                        assert "[Video]" in actual_content, f"未找到视频标识: {actual_content}"
                    elif media_type == "file":
                        file_path = expected_content['path']  # 提取路径字段
                        file_name = os.path.basename(file_path)
                        assert "[File]" in actual_content, f"未找到文件标识: {actual_content}"
                        assert file_name in actual_content, f"文件名不匹配: {file_name} vs {actual_content}"
                    # 验证时间戳
                    actual_time = session_item.find_element(*SESSION_ITEM_UPDATES_TIME).text
                    assert actual_time == expected_time, f"时间不匹配: {expected_time} vs {actual_time}"
                    # +++ 新增：验证单钩状态 +++
                    status_icon = session_item.find_element(*MSG_READ_STATUS)
                    assert status_icon.is_displayed(), "状态图标未显示"
                    #进一步严格筛选
                    icon_src = status_icon.get_attribute("src")
                    assert any(
                        status in icon_src
                        for status in [MessageStatus.SENT,MessageStatus.READ, MessageStatus.ARRIVED]
                    ), f"无效的状态图标: {icon_src}，预期包含 'read-none' 或 'read-over'"
            except Exception as e:
                raise AssertionError(f"媒体消息验证失败: {str(e)}")
    def _verify_forwarded_emojis(self,target_phone, expected_sequence):
        msg_page = MessageTextPage(self.driver)
        msg_page.open_chat_session(target='session_list', phone=target_phone)
        # 2. 复用已有验证逻辑
        assert msg_page.verify_emoji_message(expected_sequence), "表情序列不匹配"


    def select_and_forward_message(self,search_queries,
                                   select_type="list",
                                   operation_type='confirm',
                                   expected_content=None,
                                   select_count =2
                                   ):
        # 1. 选择消息
        self.select_to_message(select_count,operation_type)
        if operation_type == "delete":
            self._verify_delete_result(expected_content)
        elif operation_type == "cancel":
            WebDriverWait(self.driver, 3).until(
                EC.invisibility_of_element_located(CHECK_ELEMENT),
                message="勾选框未在5秒内消失"
            )
            self._verify_cancel_selection(expected_content)
        elif operation_type == "favorite":

            assert self.is_toast_visible('Added to Favorites'), f'未弹出{operation_type}成功的toast 提示'
            #获取当前时间用于验证
            favorite_time = datetime.now().strftime("%H:%M")
            self.card_page.open_menu_panel('favorite')
            all_items = self.base_find_elements(FAVORITE_ITEM)
            # 提取符合时间条件的收藏内容
            collected_contents = []
            for item in all_items:
                time_element = item.find_element(*FAVORITE_ITEM_TIME)
                if favorite_time in time_element.text:
                    contents = item.find_elements(By.CSS_SELECTOR, ".msg > div")
                    for msg in contents:
                     collected_contents.append(msg.text.strip())
            # 验证所有预期消息都在收藏列表里
            missing_messages =  [msg for msg in expected_content if msg not in collected_contents]
            assert not missing_messages,(
                f"部分收藏内容未找到！\n"
                f"预期收藏: {expected_content}\n"
                f"实际收藏: {collected_contents}\n"
                f"缺失消息: {missing_messages}"
            )



        else:
            print('执行confirm 多选择转发消息操作 ')
            result = self.card_page.select_friends(search_queries=search_queries, select_type=select_type)
            if operation_type == "confirm":
                share_time = self.card_page.confirm_share()
                self._verify_select_forward_result(
                    expected_names=result['expected_names'],
                    expected_content=expected_content,  # 使用处理后的内容
                    expected_time=share_time
                )


    def _get_visible_checkboxes(self):
        """获取可见勾选框（将列表倒序排列，最新消息在前）"""
        return WebDriverWait(self.driver, 5).until(
            EC.visibility_of_all_elements_located(CHECK_ELEMENT)
        )[::-1]

    def select_to_message(self,select_count,operation_type):
        latest_element = self._get_latest_message_element()
        context_element = latest_element.find_element(By.CSS_SELECTOR, '.whitespace-pre-wrap')
        ActionChains(self.driver).context_click(context_element).perform()
        self._select_context_menu('Multiple')
        checkboxes = self._get_visible_checkboxes()
        # 勾选前 select_count 条（从最新开始）
        # 勾选前一条消息
        if select_count>1:
            for i in range(1,select_count):
                if i<len(checkboxes):
                    if not checkboxes[i].is_selected():
                        checkboxes[i].click()
        if operation_type == "delete":
            self.base_click(SELECT_DELETE)
            time.sleep(0.5)
            self.base_click(CONFIRM_SELECT_DELETE)
        elif operation_type == "cancel":
            self.base_click(SELECT_CLOSE)
        elif operation_type == "favorite":
            self.base_click(SELECT_FAVORITE)
        else:
            self.base_click(SELECT_FORWARD)


    def _verify_select_forward_result(self,expected_names,expected_content,expected_time):
        for name in expected_names:
            print('验证单聊中',name,'预期数量：',len(expected_content))
            self.msg_page.open_chat_session(target='session_list', phone=name) #打开每个勾选的单聊页面
            time.sleep(3)
            # 2. 根据最新两条定位消息项+时间一致+单钩状态
            # 2. 直接定位最新两条消息（避免获取全部） # 根据预期内容数量获取消息
            expected_count = len(expected_content)
            messages = self.get_last_n_messages(expected_count)
            print('验证单聊中得到数据',messages,expected_content)
            # 3. 验证消息数量
            assert len(messages) == expected_count, (
                f"消息数量不符，预期{expected_count}条，实际{len(messages)}条"
            )
            actual_contents = []
            for msg in messages:
                try:
                    print(msg.get_attribute('outerHTML'))
                    content = msg.find_element(By.CSS_SELECTOR, ".whitespace-pre-wrap").text.strip()
                    print('获取到其中一条消息：',content)
                    actual_contents.append(content)
                except NoSuchElementException:
                    continue  # 忽略非文本消息
                    # 4. 验证每个预期内容存在
            print("添加到了actual_contents：", actual_contents)
            actual_set = set(actual_contents)
            expected_set = set(expected_content)
            assert actual_set == expected_set, (
                f"转发消息内容不匹配\n"
                f"预期内容（无序）: {expected_set}\n"
                f"实际内容（无序）: {actual_set}"
            )
    def _get_message_by_index(self,index):
        return  WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, f"article.chat[index='{index}']")
        )
    )

    def get_last_n_messages(self,n):
        try:
            # 确保在聊天窗口中查找 而不是会话列表
            messages = []
            latest_index = self.msg_page.latest_msg_index_in_chat()
            print(f"单聊中最新index：{latest_index}")

            # 计算起始索引（最新消息往前推n-1条）
            start_index = max(0, latest_index - n + 1)

            # 遍历索引范围（包含最新消息）
            for idx in range(start_index, latest_index + 1):
                try:
                    element = self._get_message_by_index(idx)
                    messages.append(element)
                except (TimeoutException, NoSuchElementException):
                    # 允许部分消息缺失（如测试环境消息被清理）
                    continue
            return messages
        except NoSuchElementException:
            return []  # 返回空列表避免后续操作报错
    def get_group_n_message(self,n):
        try:
            # 确保在聊天窗口中查找
            message = []

            # 查找聊天窗口中的所有消息
            chat_messages = self.driver.find_elements(By.CSS_SELECTOR, "div[index] > article.chat")

            # 获取最新的n条消息
            for i in range(max(0, len(chat_messages) - n), len(chat_messages)):
                message.append(chat_messages[i])

            return message

        except Exception as e:
            print(f"获取消息时出错: {e}")
            return []
    def _verify_delete_result(self,expected_content):
        # 获取删除后的消息列表
        expected_count = len(expected_content)
        messages = self.get_last_n_messages(expected_count)
        actual_contents = []
        for msg in messages:
            content = msg.find_element(By.CSS_SELECTOR, ".whitespace-pre-wrap").text.strip()
            actual_contents.append(content)
        print("检测删除后最新2条/预期", actual_contents, expected_content)
        for content in expected_content:
            assert content not in actual_contents, f"消息'{content}'未被成功删除"
    def _verify_cancel_selection(self,expected_content):
        latest_element = self._get_latest_message_element()
        content = latest_element.find_element(By.CSS_SELECTOR, ".whitespace-pre-wrap").text.strip()
        print(content,expected_content)
        assert expected_content[0] == content, "原消息元素不见了"

    #消息删除————————————
    def delete_to_message(self,expected_content,operation_type):
        latest_element = self._get_latest_message_element()
        context_element = latest_element.find_element(By.CSS_SELECTOR, '.whitespace-pre-wrap')
        ActionChains(self.driver).context_click(context_element).perform()
        self._select_context_menu('Delete')
        time.sleep(0.5)
        if operation_type == "cancel":
            self.base_click(CANCEL_SHARE)
            self._verify_cancel_selection(expected_content)
        else:
            self.base_click(CONFIRM_SELECT_DELETE)
            self._verify_delete_result(expected_content)

    # 消息撤回————————————
    def recall_to_message(self,media_type='text'):
        # 记录原消息索引
        original_index = self.msg_page.latest_msg_index_in_chat()
        latest_element = self._get_latest_message_element()
        context_element = self._get_context_element(latest_element, media_type if media_type else 'text')
        ActionChains(self.driver).context_click(context_element).perform()
        self._select_context_menu('Recall')
        self._verify_recall_result(original_index)

    def _verify_recall_result(self,original_index):
        # 尝试获取原消息元素
        original_element = self.driver.find_element(
            By.CSS_SELECTOR,
            f"article.chat[index='{original_index}']"
        )
        print('撤回后的消息',original_element.text)
        assert "You recalled a message" in original_element.text
    # 消息编辑————————————
    def edit_to_msg(self,new_content,operation_type):
        latest_element = self._get_latest_message_element()
        context_element = latest_element.find_element(By.CSS_SELECTOR, '.whitespace-pre-wrap')
        ActionChains(self.driver).context_click(context_element).perform()
        self._select_context_menu('Edit')
        self.msg_page.enter_message(new_content)
        time.sleep(0.5)
        if operation_type == "cancel":
            self.base_click(QUOTE_BOX_CLOSE)
        self.msg_page.send_message()
        self._verify_edit_result(new_content,operation_type)

    def _verify_edit_result(self,new_content,operation_type):

        latest_element = self._get_latest_message_element()
        context_element = latest_element.find_element(By.CSS_SELECTOR, '.whitespace-pre-wrap')
        actual_content = context_element.text
        assert actual_content == new_content[0], f"内容未更新！预期: {new_content[0]}，实际: {actual_content}"
        try:
            index = self.msg_page.latest_msg_index_in_chat()
            latest_element = self.driver.find_element(
                By.CSS_SELECTOR,
                f"div[index='{index}']"
            )
            edited_tag  = latest_element.find_element(*EDIT_TIP)
            edited_text = edited_tag.text
            is_edited_visible = edited_tag.is_displayed()
        except NoSuchElementException:
            is_edited_visible = False
            edited_text = ""
        if operation_type == "cancel":
            assert not is_edited_visible, f"取消编辑后仍显示编辑标记，内容: {edited_text}"
        else:
            # 确认编辑时应显示 Edited 标签
            assert is_edited_visible, "编辑后未显示编辑标记"
            assert edited_text.strip() == "Edited", f"编辑标记文本异常，预期'Edited'，实际'{edited_text}'"

    # 消息复制————————————
    def copy_to_message(self,operations,message_content,media_type,file_paths):
        before_index = self.msg_page.latest_msg_index_in_chat()
        latest_element = self._get_latest_message_element()
        context_element = self._get_context_element(latest_element, media_type if media_type else 'text')
        ActionChains(self.driver).context_click(context_element).perform()
        self._select_context_menu('Copy')
        for op in operations:
            self.msg_page.perform_operation(action_type=op)
            time.sleep(0.5)
        # if media_type == "text" or media_type == "emoji":
        self.msg_page.send_message()
        # else:
        #     self.msg_page.handle_file_upload(timeout=2)
        # print("消息索引变化:", before_index, after_index)
        # assert self._verify_copy_result(message_content,media_type,file_paths)
        result, error_message = self._verify_copy_result(message_content, media_type, file_paths)
        assert result, error_message
        after_index = self.msg_page.latest_msg_index_in_chat()
        assert after_index > before_index, "消息index未增加，复制操作可能失败"

    def _verify_copy_result(self,message_content,media_type,file_paths):
        print("验证内容:", message_content, media_type, file_paths)
        latest_element = self._get_latest_message_element()
        context_element = self._get_context_element(latest_element, media_type if media_type else 'text')
        processed_content = message_content[0] if media_type != "emoji"  else message_content
        if media_type == "emoji":
            result = self.msg_page.verify_emoji_message(processed_content)
            return result, "表情序列不匹配"
        elif media_type == "text":
            print(f"验证: 预期='{processed_content}' | 实际='{context_element.text}'")
            result = context_element.text == processed_content
            return result, f"内容未更新！预期: {message_content}，实际: {context_element.text}"
        else:
            result = self.msg_page.verify_media_message(media_type,file_paths,timeout=2)
            return result, '媒体类型验证失败'

    # 消息收藏————————————
    def favorite_to_message(self,message_content,media_type,test_id=None):
        """
           收藏消息（新增test_id参数但不影响原有逻辑）
           """
        print('接收media_type：',media_type)
        latest_element = self._get_latest_message_element()
        # context_element = latest_element.find_element(By.CSS_SELECTOR, '.whitespace-pre-wrap')
        # ActionChains(self.driver).context_click(context_element).perform()
        # self._select_context_menu('Favorite')
        # self.open_menu_panel("favorite")
        # 根据不同类型选择上下文元素
        if media_type == 'text' or media_type == 'emoji':
            context_element = latest_element.find_element(By.CSS_SELECTOR, '.whitespace-pre-wrap')
        elif media_type == 'image':
            context_element = latest_element.find_element(By.CSS_SELECTOR, '.img')
        elif media_type == 'video':
            context_element = latest_element.find_element(By.CSS_SELECTOR, '.video')
        else: # 文件或其他类型
            context_element = latest_element.find_element(By.CSS_SELECTOR, '.file')
        # 执行右键操作
        try:
            ActionChains(self.driver).context_click(context_element).perform()
            self._select_context_menu('Favorite')
            # 获取当前时间（精确到分钟）
            favorite_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            # 从文件路径提取预期特征 (如 "src/imgs/anime.jpg" -> "1-thumbnail")

            # 优化日志输出（区分是否有test_id）
            log_msg = f"✅ 成功收藏 [{media_type}] 消息，时间: {favorite_time}"
            print(log_msg)
            return favorite_time,True
        except Exception as e:
            print(f"收藏消息失败: {str(e)}")
            if test_id:
                print(f"Error occurred while 正在收藏的消息时发送错误， ID是: {test_id}")
            return None,False

    def verify_result_favorite(self,media_type,favorite_time,test_id=None, expected_src_parts=None,expected_emojis=None):
        """
               通过test_id或内容验证收藏消息是否存在
        """

        self.base_find_element(FAVORITE_RIGHT_LIST)
            # 查找所有收藏项
        all_items = self.base_find_elements(FAVORITE_ITEM)
        for item in all_items:
            try:
                #检查时间是否匹配
                time_element = item.find_element(*FAVORITE_ITEM_TIME)
                user_element= item.find_element(*FAVORITE_ITEM_NAME)
                print(f'传过来的时间是：{favorite_time} 获取到的是：{time_element.text}')
                # print(f'传过来的时间-用户是：{favorite_time}-{target_chat} 获取到的是：{time_element.text}-{user_element.text}')
                if favorite_time  not in time_element.text:
                    continue
                # # 2. 检查用户是否匹配
                # if target_chat not in user_element.text:
                #     continue


                #根据媒体类型验证
                content = item.find_element(*FAVORITE_ITEM_CONTENT)

                if media_type =='text' and test_id:
                    # 文本消息检查ID
                    if f"[ID:{test_id}]" in content.text:
                        return True
                elif media_type == 'file':
                    doc_loc = content.find_elements(By.CSS_SELECTOR, '.col-left')
                    doc_name = doc_loc[0].text
                    if expected_src_parts[0] in doc_name:
                        return True
                elif media_type == 'emoji' and expected_emojis:
                    emoji_imgs  = content.find_elements(By.TAG_NAME,'img')
                    emoji_srcs = [emoji.get_attribute('src') for emoji in emoji_imgs]
                    print('得到：',emoji_srcs)
                    for name in expected_emojis:
                        if not any(f'emoji_{name}' in src for src in emoji_srcs):
                            print(f"未找到预期表情 '{name}'，实际SRC列表: {emoji_srcs}")
                            return False
                    print("所有预期表情验证成功")
                    return True

                else:
                    media_element =  content.find_element(By.TAG_NAME,'img')
                    src = media_element.get_attribute('src')
                    if src and expected_src_parts:
                        print('得到的src:',src,'得到的expected_src:',expected_src_parts)
                        # # 检查src是否包含所有预期的特征 不检查后缀
                        if all(part in src for part in expected_src_parts):
                            return True

                        elif not expected_src_parts:
                            # 如果没有提供特征，只要找到对应标签就返回True
                            return False

            except NoSuchElementException as e:
                print(f'验证过程中元素未找到: {str(e)}')
                continue
        print(f"未找到匹配的收藏项: 时间[{favorite_time}]  类型[{media_type}]")
        if expected_src_parts:
            print(f"期望的src特征: {expected_src_parts}")
        return False

    def _find_favorite_item(self, media_type, file_base_name, favorite_time):
        """查找匹配的收藏项"""
        all_items = self.base_find_elements(FAVORITE_ITEM)  # 所有收藏项
        for item in all_items:
            try:
                #检查时间匹配项
                time_element = item.find_element(*FAVORITE_ITEM_TIME)
                if favorite_time not in time_element.text:
                    continue
                #检查内容匹配
                content = item.find_element(*FAVORITE_ITEM_CONTENT)
                if media_type =='text':
                    if file_base_name in content.text:
                        print(f"[DEBUG] 找到{media_type}收藏项:{content.text}")
                        return item
                elif media_type in ['image', 'video']:
                    imgs = content.find_elements(By.TAG_NAME, 'img')
                    if imgs:
                        img = imgs[0]  # 取第一个 <img> 元素（WebElement对象）
                        src = img.get_attribute('src')  # ✅ 这才是正确的！
                        if file_base_name.lower() in src.lower():
                            return item
                elif media_type == 'emoji':
                    emojis = content.find_elements(By.TAG_NAME, 'img')
                    for img in emojis:
                        if 'emoji_' in img.get_attribute('src').lower():
                            continue
                    return item
                elif media_type == 'file':
                    file_name = item.find_element(*VIEW_CONTENT_FILE)
                    # file_name = self.base_find_elements(VIEW_CONTENT_FILE)
                    # file_name1 = file_name[0].text
                    if file_base_name in file_name.text:
                        print(f"[DEBUG] 找到{media_type}收藏项:{file_name.text}")
                        return item
            except NoSuchElementException:
                continue
        print(f'没有找到刚收藏的{media_type}类型消息')
        return None

    def _handle_viewer_window(self, media_type,keyword,file_base_name):
        """处理查看详情窗口"""
        main_window = self.driver.current_window_handle
        viewer_window = None
        try:
            # 根据类型切换到对应的查看器窗口
            if media_type == 'text':
                viewer_window = self.switch_to_new_window_by_feature((By.CSS_SELECTOR, "main.content"))
                actual_txt_name = self.base_find_element((By.CSS_SELECTOR, ".whitespace-pre-wrap")).text
                assert file_base_name in actual_txt_name, f"收藏的文件名不匹配！实际：{actual_txt_name}，期望：{file_base_name}"

            elif media_type == 'file':
                viewer_window = self.switch_to_new_window_by_feature((By.CSS_SELECTOR, "main.content"))
                actual_file_name = self.base_find_element((By.CSS_SELECTOR, ".file-name")).text
                assert file_base_name in actual_file_name, f"收藏的文件名不匹配！实际：{actual_file_name}，期望：{file_base_name}"
            elif media_type == 'image':
                # 3. 切换到图片查看器窗口
                viewer_window = self.switch_to_new_window_by_feature((By.CSS_SELECTOR, "main.image-editor"))
                displayed_file_name = self.base_find_element(VIEW_CONTENT_NAME).text
                assert keyword == displayed_file_name, f"文件名不一致，期望包含 {keyword}，实际是 {displayed_file_name}"
                content = self.base_find_element(VIEW_CONTENT_IMAGE)
                main_img = content.find_element(By.TAG_NAME, "img")
                is_loaded = self.driver.execute_script(
                    "return arguments[0].complete && arguments[0].naturalWidth > 0;", main_img
                )
                assert is_loaded, f"{media_type}未正确加载，可能裂图或 404，src = {main_img.get_attribute('src')}"
                main_src = main_img.get_attribute('src')
                assert keyword in main_src.lower(), f"新页面图片 src 似乎不是预期的文件，src = {main_src}"

            elif media_type == 'video':
                viewer_window = self.switch_to_new_window_by_feature((By.CSS_SELECTOR, "main.video-preview"))
                # 等待内容加载
                displayed_file_name = self.base_find_element(VIEW_CONTENT_NAME).text
                assert keyword == displayed_file_name, f"文件名不一致，期望包含 {keyword}，实际是 {displayed_file_name}"
                content = self.base_find_element(VIEW_CONTENT_VIDEO)
                main_img = content.find_element (By.TAG_NAME, "video")
                is_loaded = self.driver.execute_script(
                    "return arguments[0].readyState > 0 && arguments[0].duration > 0;", main_img
                )
                assert is_loaded,f"{media_type}未正确加载，可能裂图或 404，src = {main_img.get_attribute('src')}"
                main_src = main_img.get_attribute('src')
                assert  keyword in main_src.lower(),f"新页面图片 src 似乎不是预期的文件，src = {main_src}"
            # 关闭查看窗口
            time.sleep(3)
            self.driver.close()
            self.driver.switch_to.window(main_window)
        except Exception as e:
            print(f"处理查看窗口失败: {str(e)}")
            raise
        finally:
            time.sleep(3)
            #清理窗口
            current_handles = self.driver.window_handles
            # 优先关闭图片查看器窗口
            if viewer_window in current_handles:
                self.driver.switch_to.window(viewer_window)
                self.driver.close()
                print("已关闭查看详情窗口")
            if main_window in current_handles:
                self.driver.switch_to.window(main_window)
            else:
                print("警告：主窗口丢失，切换到第一个可用窗口")
                self.driver.switch_to.window(current_handles[0])

    def view_favorite_item(self,media_type, keyword, favorite_time):
        """查看收藏项详情"""
        self.open_menu_panel("favorite")
        if media_type in ['text', 'emoji']:
            file_base_name = keyword
        else:
            file_base_name = os.path.splitext(keyword)[0]  # 获取anime或1
        # 确保元素可见
        item = self._find_favorite_item(media_type, file_base_name, favorite_time)
        if not item:
            raise Exception(f"未找到匹配的收藏项: {file_base_name}")
        # 点击查看
        if media_type in ['image', 'video']:
            item.find_element(By.TAG_NAME, 'img').click()
        elif media_type == 'file':
            item.click()
        elif media_type == 'text':
            item.click()
        # 处理新窗口
        time.sleep(2)
        self._handle_viewer_window(media_type,keyword,file_base_name)

    def delete_favorite_item(self,media_type,keyword,favorite_time,toast_message):
        self.open_menu_panel("favorite")
        item = self._prepare_item(media_type,keyword,favorite_time)
        # 右键点击收藏项
        self._execute_item_action(item,action_type ='Delete')
        # ActionChains(self.driver).context_click(item).perform()
        # time.sleep(1)
        # # 选择转发菜单
        # self._select_context_menu('Delete')
        self.card_page.confirm_share()
        is_success = self.is_toast_visible(toast_message)
        assert is_success, f"❌ 【删除】操作后未检测到「删除成功」提示弹窗"


    # 新增基础方法
    def _prepare_item(self, media_type, keyword, favorite_time=""):
        """准备收藏项(公共方法)"""
        file_base_name = keyword if media_type in ['text', 'emoji'] else os.path.splitext(keyword)[0]
        item = self._find_favorite_item(media_type, file_base_name, favorite_time)
        if not item:
            raise ValueError(f"未找到匹配的收藏项: {keyword}")

        self.driver.execute_script("arguments[0].scrollIntoView();", item)
        time.sleep(1)
        return item

    def _execute_item_action(self, item, action_type):
        """执行右键操作(公共方法)"""
        ActionChains(self.driver).context_click(item).perform()
        time.sleep(1)
        self._select_context_menu(action_type)
        time.sleep(1)


    def forward_favorite_item(self, media_type, keyword, favorite_time, search_queries):
        """转发收藏项"""


        item = self._prepare_item(media_type, keyword, favorite_time)
        self._execute_item_action(item,action_type = 'Forward')


        result = self.card_page.select_friends(search_queries, select_type="list")
        share_time = self.card_page.confirm_share()
        # # 验证转发结果
        processed_content = keyword[0] if media_type != "emoji" and isinstance(keyword,
                                                            list) else keyword
        print(keyword[0])
        self.card_page.open_menu_panel("home")
        self._verify_forward_result(
            expected_names=result['expected_names'],
            expected_content=processed_content,
            expected_time=share_time,
            media_type=media_type
        )

    def multiple_favorite(self, checks_items,action,search_queries,expected):
        selected_count = expected['selected_count']
        toast_message = expected['toast_message']
        """动态多选收藏项并转发"""
        found_items =[]
        print(f'得到勾选数据: {checks_items}和多选操作{action}')
        self.card_page.open_menu_panel("favorite")
        time.sleep(2)
        for item in checks_items:
            media_type = item['type']
            file_base_name   = item['identifier']
            print(f"确认文件名称：{file_base_name}")

            found_item = self._find_favorite_item(
                media_type=media_type,
                file_base_name=file_base_name,
                favorite_time="")
            if found_item:
                print('找到第i个元素',found_item.get_attribute("src"))
                try:
                    img_element = found_item.find_element(By.TAG_NAME, 'img')
                    img_src = img_element.get_attribute("src")
                    print('图片src:', img_src)
                except Exception as e:
                    print('未能找到 img 元素:', str(e))
                found_items.append(found_item)
        print(f"找到 {len(found_items)} 个匹配的收藏项,{found_items}")
        if len(found_items) != len(checks_items):
            raise ValueError(f"未找到所有匹配项，预期 {len(checks_items)} 个，实际找到 {len(found_items)} 个")
        if len(found_items) >= len(checks_items):
            try:
                self._execute_item_action(found_items[0],action_type='Multiple')
                # ActionChains(self.driver).context_click(found_items[0]).perform()# 右键点击收藏项
                # time.sleep(1)
                # self._select_context_menu('Multiple')
                checkbox = found_items[1].find_element(*CHECKBOX)  # 勾选第二个元素的复选框.check
                if not checkbox.is_selected():
                    checkbox.click()

                # 执行转发操作
                if action == 'forward':
                    self.base_click(SELECT_FAVORITE)
                    result = self.card_page.select_friends(search_queries, select_type="list")
                    share_time = self.card_page.confirm_share()

                    assert self.is_toast_visible(toast_message),"未检测到转发成功的 toast 提示"
                    self.card_page.open_menu_panel("home")
                    for name in result['expected_names']:
                        self.msg_page.open_chat_session(target='session_list', phone=name)  # 打开每个勾选的单聊页面
                        messages = self.get_last_n_messages(selected_count)  # print('获取实际最新2条消息元素/预期值',messages,expected_content)
                        print('得到最新的两条消息元素',messages)

                        # 3. 验证消息数量
                        assert len(messages) == selected_count, (
                            f"消息数量不符，预期{selected_count}条，实际{len(messages)}条"
                        )
                        # 5.2 直接使用收藏项的类型和 identifier 进行匹配
                        type = checks_items[0]['type']
                        div_type =None
                        if type == 'video':
                            div_type = 'video'
                        elif type == 'image':
                            div_type = 'img'
                        identifier = checks_items[0]['identifier']
                        actual_messages=[]
                        for msg in messages:
                            actual_time = msg.find_element(*CONTENT_TIME)
                            assert actual_time.text.strip() ==share_time, '发送消息时间和不一致'
                            video_elements = msg.find_elements(By.CSS_SELECTOR,f"div.{div_type} img")
                            if video_elements:
                                src = video_elements[0].get_attribute("src")
                                #从src中提取文件名（例如获取最后一个 / 后的内容）
                                filename = src.split('/')[-1].split('?')[0]  # 处理可能有的查询参数
                                print("视频src值:", filename)
                                key = identifier.split('-')[0]  # 得到 "audio"
                                if key in src.lower():
                                    actual_messages.append({'type': type, 'identifier': identifier})
                                    continue
                            # 判断是否为文件消息
                            file_name_elements = msg.find_elements(By.CSS_SELECTOR, ".file-name")
                            if file_name_elements:
                                file_name = file_name_elements[0].text  # 直接获取文件名（如 document.docx）
                                print(f"得到文件{file_name}")
                                actual_messages.append({'type': 'file', 'identifier': file_name})
                            # 2. 验证是否覆盖所有收藏项
                        for expected_item in checks_items:
                            if expected_item not in actual_messages:
                                raise AssertionError(f"未找到预期消息: {expected_item}")
                elif action == 'cancel':
                    self.base_click(SELECT_CLOSE)
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.invisibility_of_element_located(CHECKBOX)
                        )
                        print("取消操作成功：勾选框已消失")
                    except TimeoutException:
                        raise AssertionError("取消操作失败：勾选框未在预期时间内消失")

                elif action == 'delete':
                    self.base_click(SELECT_FORWARD)

                    self.card_page.confirm_share()
                    assert self.is_toast_visible(toast_message),"未检测到转发成功的 toast 提示"
                    time.sleep(1)  # 可优化为显式等待
                    for item in found_items:

                        try:
                            WebDriverWait(self.driver, 5).until(
                                EC.staleness_of(item)  # 检查元素是否从DOM移除
                            )
                        except TimeoutException:
                            raise AssertionError(f"删除失败：元素仍存在")
                    print("删除操作验证通过：所有目标项已移除")



            except Exception as e:
                print(f"操作过程中出错: {str(e)}")
                raise
    def is_toast_visible(self,message):
        try:
            toast  = self.wait.until( EC.visibility_of_element_located(TIP_SUCCESS))
            toast_message = toast.find_element(By.CSS_SELECTOR,'.el-message__content').text
            return message in toast_message
        except Exception as e:
            print(f"Error occurred: {e}")
            return False

    def _count_items_by_category(self):
        """统计各类收藏数量(私有方法)"""
        category_stats={
            "text": 0,
            "emoji": 0,
            "image": 0,
            "file": 0
        }
        all_items = self.base_find_elements(FAVORITE_ITEM) # 所有收藏项
        for item  in all_items:
            try:
                # 通过元素特征判断类型
                if item.find_elements(By.CSS_SELECTOR, ".text-content, [class*='break-all'] div"):
                    category_stats["text"] += 1
                if item.find_elements(By.CSS_SELECTOR, ".col-left"):
                    category_stats["file"] += 1

                emoji_container = item.find_elements(By.CSS_SELECTOR, "img[src*='emoji_']")
                if emoji_container:
                    category_stats["emoji"] += 1

                # 3. 识别媒体内容（图片/视频）
                media_element = item.find_elements(By.CSS_SELECTOR, ".break-all.relative img, video")
                if media_element:
                    category_stats["image"] += 1
            except NoSuchElementException:
                continue
        return category_stats

    def verify_favorite_categories(self):
        self.open_menu_panel('favorite')
        time.sleep(1)
        # 1. 首先在全部收藏中统计各类数量
        category_stats = self._count_items_by_category()
        print(f"全部收藏统计: {category_stats}")
        # 2. 验证各分类项
        categories = [
            {"name": "all", "locator": (By.CSS_SELECTOR, ".side-item .icon-all-collect")},
            {"name": "media", "locator": (By.CSS_SELECTOR, ".side-item .icon-img-video")},
            {"name": "file", "locator": (By.CSS_SELECTOR, ".side-item .icon-collect-file")}
        ]
        for category in categories:
            self.base_click(category["locator"])
            time.sleep(1)  # 等待内容加载
            # 获取当前分类下的实际数量
            current_items = self.driver.find_elements(*FAVORITE_ITEM)
            actual_count = len(current_items)
            # 获取预期数量
            if category["name"] == "all":
                expected_count = sum(category_stats.values())
            elif category["name"] == "media":
              expected_count = category_stats["image"]
            else:  # file
                expected_count = category_stats["file"]
            # 验证数量
            assert actual_count == expected_count, (
                f"{category['name']}分类数量不匹配，预期{expected_count}，实际{actual_count}"
            )
            print(f"✅ {category['name']}分类验证通过")
        return True

    def clear_favorites(self):
        try:
            self.card_page.open_menu_panel('favorite')
            # messages = self.get_last_n_messages(1)

            items = self.driver.find_elements(*FAVORITE_ITEM)
            if not items:
                print("没有需要清理的收藏项")
                return True
            latest_item = self.driver.find_elements(By.CSS_SELECTOR, 'div[index="0"] .collection-item')
            ActionChains(self.driver).context_click(latest_item[0]).perform()# 右键点击收藏项
            time.sleep(1)
            self._select_context_menu('Multiple')
            checkboxes = self.driver.find_elements(By.CSS_SELECTOR, '.check')
            if checkboxes:
                for check in checkboxes[1:]:
                    if not check.is_selected():
                        check.click()
                self.base_click(SELECT_FORWARD)
                self.card_page.confirm_share()
                assert self.is_toast_visible("Delete Success"),"未清空收藏管理中的消息tip 提示"
                return True  # 清空成功
                time.sleep(2)
        except Exception as e:
                print(f"清空收藏时发生异常: {e}")
                return False


















