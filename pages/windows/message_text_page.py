import fnmatch
import os
import time
from operator import index
from time import sleep

import pyperclip
import pytest
import win32clipboard
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from  selenium.webdriver.support import  expected_conditions as EC
from base.electron_pc_base import ElectronPCBase
from pages.windows.card_message_page import CardMessagePage
from pages.windows.loc.message_locators import MY_AVATAR, AVATAR_MENU, AVATAR_MESSAGE_Button, TEXTAREA_INPUT, \
    Message_Send, PHONE_LOC, CURRENT_WINDOW_PHONE, ALL_TEXT, ALL_MESSAGE, MENU_ITEMS, SEARCH_INPUT, SEARCH_SECTION, \
    SESSION_LIST, SESSION_ITEMS, SESSION_PHONE, CONTACTS_ICON, CONTACTS_CONTAINER, FRIEND_CARD, SEND_MSG_BUTTON, \
    FRIEND_NAME, FRIEND_BUTTON, FILE_INPUT, UPLOAD_FILE, DIALOG_FILE, DIALOG_FILE_CONFIRM, FILE_CONTAINER, \
    IMAGE_CONTAINER, VIDEO_CONTAINER, FILE_NAME, EMOJI_POPUP_SELECTOR, EMOJI_ICON, VOICE_MESSAGE_BTN, \
    VOICE_MESSAGE_CONTAINER
from selenium.common.exceptions import TimeoutException


# pages/windows/message_text_page.py

class MessageTextPage(ElectronPCBase):

    def __init__(self, driver):
        super().__init__()  # 调用父类构造函数
        self.driver = driver  # 设置 driver
        self.wait = WebDriverWait(driver, 10, 0.5)
        self.card_page = CardMessagePage(self.driver)  # 直接复用已有页面对象




    def get_current_phone_number(self):
        self.base_click(MY_AVATAR)
        login_phone = self.base_get_text(PHONE_LOC)
        return login_phone

    def open_avatar_menu(self):
        # self.base_click(MY_AVATAR)
        self.base_find_element(AVATAR_MENU)
        message_btn = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable(AVATAR_MESSAGE_Button)
        )
        message_btn.click()
        print("已点击发消息按钮")

    #验证窗口的账号是否和预期的一致
    def verify_message_window_phone(self,expected_phone):
        current_window_phone=self.base_get_text(CURRENT_WINDOW_PHONE)
        print('当前窗口的手机号是：',current_window_phone)
        self.logger.info(f"当前单聊的账号是：{current_window_phone}")
        if current_window_phone == expected_phone:
            self.logger.info(f"发消息窗口的手机号验证成功: {expected_phone}")
            return True
        else:
            self.logger.info(f'预期登入的账号是{expected_phone},但实际单聊账号是{current_window_phone}')
            return False

    def enter_message(self,message):
        # 检测是否处于引用模式
        is_quote_mode = self.driver.find_elements(By.CLASS_NAME, "quote-box")
        if is_quote_mode:
            print('引用')
            self.base_input_quto_text(TEXTAREA_INPUT,message)
        else:
            print('非引用')
            self.base_input_text(TEXTAREA_INPUT,message)
    def send_message(self):
        self.base_click(Message_Send)
    def delete_message(self):
        self.handle_keyboard_event('delete',TEXTAREA_INPUT)
    def copy_message(self):
        self.handle_keyboard_event('copy',TEXTAREA_INPUT)
    def paste_message(self):
        self.handle_keyboard_event('paste',TEXTAREA_INPUT)

        #获取聊天框内文本框的最新index
    def latest_msg_index_in_chat(self):
        try:
            all_messages = self.base_find_elements(ALL_MESSAGE)
            if not all_messages:
                return None
            if all_messages:
                latest_index = max([int(msg.get_attribute('index')) for msg in all_messages]) #获取最大index
                # print('最大index是',latest_index)
                return latest_index
            else:
                print('单聊框内消息列表为空')
                return None
        except Exception as e:
            print(f"获取单聊框内最新消息 index 时出错: {e}")
            return None
        #通过最新index获取最新消息
    def latest_message_by_index_in_chat(self):
        try:
            # 获取最新消息的 index
            latest_index = self.latest_msg_index_in_chat()
            if latest_index is None:
                return None

            # 通过 index 定位最新消息
            latest_message = self.driver.find_element(
                By.CSS_SELECTOR, f".chat-message div[index='{latest_index}'] .whitespace-pre-wrap"
            )
            return latest_message.text.strip()
        except Exception as e:
            print(f"通过 index 获取单聊框内最新消息时出错: {e}")
            return None

    def wait_for_latest_message_in_chat(self, timeout=30,except_type='text'):
        """
        等待单聊框内最新消息加载完成
        :param timeout: 超时时间
        :return: 最新消息的文本内容
        """
        try:
            # 先等待消息发送完成（观察消息列表稳定） 至少有一条消息存在
            WebDriverWait(self.driver, timeout).until(
                lambda d: len(self.base_find_elements(ALL_MESSAGE)) > 0
            )
            # 获取最新消息的 index
            latest_index = self.latest_msg_index_in_chat()
            print(f"最终使用index: {latest_index}")

            if latest_index is None:
                return None

            #最新位置的不同类型loc [1]是解构到元素
            slector_map = {
                'text':f"div[index='{latest_index}'] .whitespace-pre-wrap ",
                'file':f"div[index='{latest_index}'] {FILE_CONTAINER[1]} ",
                'image':f"div[index='{latest_index}'] {IMAGE_CONTAINER[1]} ",
                'video':f"div[index='{latest_index}'] {VIDEO_CONTAINER[1]} ",
                'voice':f"div[index='{latest_index}'] {VOICE_MESSAGE_CONTAINER[1]}",
                'quote':f"div[index='{latest_index}'] .cite " # 新增引用消息容器选择器

            }
            locator = (By.CSS_SELECTOR,slector_map[except_type])
            print(f"等待加载选择器: {locator}")  # Debug信息
            # 等待最新消息加载
            time.sleep(2)

            latest_message = self.base_find_element(locator)
            print('获取到了最后一个对应的内容：',latest_message)
            # 滚动到可视区域
            self.driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", latest_message)

            time.sleep(1)
            #考虑到表情要单独做返回处理
            message_text = latest_message.text.strip() if except_type == 'text' else None
            # 提取表情信息
            emoji_elements = latest_message.find_elements(By.TAG_NAME, 'img')
            emoji_srcs = [emoji.get_attribute('src') for emoji in emoji_elements]
            # 返回消息文本、表情信息和m媒体元素
            # return latest_message.text.strip() if except_type == 'text' else latest_message
            return {
                'text':message_text,
                'emoji':emoji_srcs,
                'latest_message_element':latest_message
            }

        except Exception as e:
            print(f"等待单聊框内最新消息时出错: {e}")
            return None

    def is_text_message_in_chat(self, message, timeout=10):
        """
        验证单聊框内最新文本消息是否包含指定内容   等待最新消息加载
        :param message: 需要验证的消息内容
        :param timeout: 超时时间
        :return: True 如果找到最新文本消息并匹配内容，否则 False
        """
        result  = self.wait_for_latest_message_in_chat(timeout,except_type='text')
        if not result or not['text']:
            print("未找到最新文本消息")
            return False
        latest_text=result['text']
        # 验证消息内容
        if message == latest_text:
            print(f"文本消息 '{message}' 在聊天窗口中验证成功")
            #验证加载图标是
            latest_index = self.latest_msg_index_in_chat()
            if latest_index is None:
                return None

            if message == latest_text:
                print(f"文本消息 '{message}' 在聊天窗口中验证成功")
                return True
        else:
            print(f"最新文本消息内容为 '{latest_text}'，与预期消息 '{message}' 不匹配")
            return False

    def verify_media_message(self,media_type,file_paths=None, timeout=20):
        try:
            result  = self.wait_for_latest_message_in_chat(
                timeout=timeout,
                except_type=media_type
            )
            if not result:
                print(f"未找到{media_type}类型消息元素",result)
                return False
            element = result['latest_message_element']
             # 根据类型调用具体验证
            if media_type == 'file':
                return self._verify_file_message(file_paths, element)
            elif media_type == 'image':
                print('得到wait_for的图片：', element)
                return self._verify_image_message(file_paths, element)
            elif media_type == 'video':
                return self._verify_video_message(element)
            return False
        except Exception as e:
            print(f"媒体验证失败: {str(e)}")
            return False



    def _verify_file_message(self,file_paths,element):
        """验证文件消息"""
        try:
            #验证文件容器是否可见
            if not element.is_displayed():
                print("文件容器不可见")
                return False
            # 验证所有文件名
            names_elements = WebDriverWait(self.driver, 10).until(
                lambda d: element.find_elements(*FILE_NAME)
            )
            print('测试所有文件名：',names_elements)
            displayed_names = [el.text for el in names_elements]
            print('测试所有文件名displayed_names：', displayed_names)
            # 3. 验证文件数量匹配
            if len(file_paths) != len(displayed_names):
                print(f"文件数量不匹配，预期{len(file_paths)}，实际{len(displayed_names)}")
                return False

            for path in file_paths:
                filename = os.path.basename(path)
                # 解析预期文件的基础部分和扩展名
                # 生成基础匹配模式（如：document.docx 匹配 document*.docx）
                base_name, ext = os.path.splitext(filename)
                pattern = f"{base_name}*{ext}"  # 例如：document*.docx
                # if filename not in displayed_names: #display_names是页面获取的列表 filename是rsc下的文件名
                #     print(f"文件 {filename} 未找到，已显示文件: {displayed_names}")
                #     return False
                if not any(fnmatch.fnmatch(name, pattern) for name in displayed_names):
                    print(f"文件 {filename} 未找到匹配项，已显示文件: {displayed_names}")
                    return False

            return True
        except Exception as e:
            print(f"文件验证失败: {str(e)}")
            return False
    def _verify_image_message(self, file_paths, element):
        """验证图片消息"""
        try:
            # 确保容器可见
            # self.driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", element)
            if not element.is_displayed():
                self.logger.error("图片容器不可见")
                return False
            # 检查图片预览
            if element.size['width'] == 0 or element.size['height'] == 0:
                print("图片尺寸为0")
                return False
                # 检查src属性是否存在
            if not element.get_attribute('src'):
                print("图片src属性为空")
                return False
            return True
            # images = WebDriverWait(self.driver, 10).until(
            #     lambda d: element.find_elements(By.TAG_NAME, 'img')
            # )
            # # 确保所有图片都加载完成
            # WebDriverWait(self.driver, 10).until(
            #     lambda d: all(
            #         d.execute_script(
            #             "return arguments[0].complete && arguments[0].naturalWidth > 0",
            #             img
            #         ) for img in images
            #     ),
            #     "图片未在10秒内完成加载"
            # )
            #
            # if len(images) < len(file_paths):
            #     print(f"图片数量不足，预期 {len(file_paths)} 实际 {len(images)}")
            #     return False
            #  #验证图片加载成功 （检查naturalWidth）
            # # 2. 验证图片加载状态
            # for img in images:
            #     is_loaded = self.driver.execute_script(
            #         """
            #     return arguments[0].complete &&
            #     arguments[0].naturalWidth > 0 &&
            #     window.getComputedStyle(arguments[0]).display !== 'none'
            # """,
            #         img)
            #     if not is_loaded:
            #         print(f"图片 {img.get_attribute('src')} 未正确加载")
            #         return False
            #     # # 验证每个图片的src属性
            #     # src = img.get_attribute("src")
            #     # if not src:
            #     #     self.logger.error("图片src属性为空")
            #     #     return False
            # return True
        except Exception as e:
            print(f"图片验证异常: {str(e)}")
            return False

    def _verify_video_message(self,element):
        """验证视频消息"""
        try:
            # 1. 验证视频容器可见
            if not element.is_displayed():
                self.logger.error("视频容器不可见")
                return False
            # 2. 获取视频元素
            # video = element.find_element(By.TAG_NAME, 'video')
            # 2. 验证缩略图
            #            "typeof arguments[0].naturalWidth != 'undefined' && " +
            thumb = element.find_element(By.TAG_NAME, "img")
            is_loaded = self.driver.execute_script(
                "return arguments[0].complete && " +
                "arguments[0].naturalWidth > 0",
                thumb)

            if not is_loaded:
                self.logger.error("视频缩略图未加载")
                return False
            # 3. 验证下载按钮
            download_btn = element.find_element(By.CSS_SELECTOR, ".play")
            if not download_btn.is_displayed():
                self.logger.error("下载按钮不可见")
                return False

            return True
        except Exception as e:
            print(f"视频验证异常: {str(e)}")
            return False




    def send_message_via_enter(self):
        self.handle_keyboard_event('enter',TEXTAREA_INPUT)


    def send_multiple_message(self,messages,send_method='click',timeout=10):
        print(f"Debug - 收到的消息内容: {messages}")  # 调试用
        print(f"Debug - 消息类型: {type(messages)}")  # 调试用
        for msg in messages:
            # self.base_clear_input(TEXTAREA_INPUT)
            self.enter_message(msg)
            # 点击发送按钮
            if send_method == 'click':
                self.send_message()
            elif send_method == 'enter':  # 🚩 新增回车发送
                self.send_message_via_enter()
            # print("消息发送成功")
            # 检测聊天窗口是否包含该内容
            if not self.is_text_message_in_chat(msg):
                print("文本消息在聊天窗口中验证成功")
                return False

            latest_index = self.latest_msg_index_in_chat()
            if latest_index is None:
                print("未找到最新消息的 index")
                # all_messages_success = False
                return False
            try:
                # 等待加载图标消失（最多等待 timeout 秒）
                WebDriverWait(self.driver, timeout).until(
                    EC.invisibility_of_element_located(
                        (By.XPATH, f".//div[@index='{latest_index}']//i[contains(@class, 'animate-spin')]")
                    )
                )
                print("消息发送成功：加载图标已消失")
            except Exception as e:
                print(f"消息'{msg}'发送失败：加载图标在 {timeout} 秒后仍然存在。错误信息: {e}")
                # raise AssertionError(f"消息发送失败：加载图标在 {timeout} 秒后仍然存在。错误信息: {e}")
                return False

        # 所有消息发送成功后才返回 True
        return True

    def perform_operation(self, action_type):
        element_input = self.base_find_element(TEXTAREA_INPUT)
        if action_type.startswith('right_click:'):
            # 处理右键操作
            action = action_type.split(':')[1]
            self._handle_right_click_action(element_input, action)
        else:
            if action_type == 'select_all':
                element_input.send_keys(Keys.CONTROL + 'a')
            elif action_type == 'copy':
                element_input.send_keys(Keys.CONTROL + 'c')
            elif action_type == 'paste':
                element_input.send_keys(Keys.CONTROL + 'v')
            elif action_type == 'cut':
                element_input.send_keys(Keys.CONTROL + 'x')
            time.sleep(0.5)  # 确保操作完成
    def _handle_right_click_action(self,element_input,action):
        #右键点击元素
        ActionChains(self.driver).context_click(element_input).perform()
        time.sleep(0.5)
        menu_items=MENU_ITEMS
        if action in menu_items:
            menu_item = self.wait.until(EC.element_to_be_clickable(menu_items[action]))
            menu_item.click()
            time.sleep(0.5)

    def open_chat_session(self,target=None,phone=None):
        self.card_page.open_menu_panel('home')
        # 如果目标是自己且已经在自己的聊天窗口，则不需要操作
        if self._is_current_chat(phone):
            print(f"当前已在 {phone} 的聊天窗口，无需重新打开")
            return
        # 否则执行正常打开流程
        if target =='me':
            self.open_avatar_menu()
        elif target =='friend':
            self._search_friend(phone)
        elif target =='session_list':
            self.scroll_to_friend_in_session(phone) #调用会话滚动方法
        elif target =='contacts_list':
            # self.open_contacts()  # 打开联系人面板
            self.open_menu_panel("contacts")
            # self.base_click(FRIEND_BUTTON)
            self.scroll_to_friend_in_contacts(phone)
            self.base_click(SEND_MSG_BUTTON)
        # 二次验证窗口是否切换成功
        if not self._is_current_chat(phone):
            raise Exception(f"无法切换到 {phone} 的聊天窗口")
        # 验证窗口
        if phone:
            self.verify_message_window_phone(phone)

    def _is_current_chat(self, expected_phone):
        """检查当前是否已经在目标聊天窗口"""
        try:
            current_phone = self.base_get_text(CURRENT_WINDOW_PHONE)
            print(f'当前窗口号码：{current_phone}，预期号码：{expected_phone}')
            return current_phone == str(expected_phone)  # 确保类型一致
        except NoSuchElementException:
            print("未找到当前聊天窗口号码元素")
            return False
        except Exception as e:
            print(f"检查当前聊天窗口时发生异常：{str(e)}")
            return False
    #会话列表中查找该好友/contact菜单好友列表——会话列表滚动查找好友
    def scroll_to_friend_in_session(self,phone,max_scroll=5 ,raise_exception=True):
        # 获取会话列表容器
        return self.scroll_to_element(
            SESSION_LIST,
            SESSION_ITEMS,
            phone,
            max_scroll,
            SESSION_PHONE,
            raise_exception=raise_exception)



    # def open_contacts(self):
    #     """打开联系人面板"""
    #     self.base_click(CONTACTS_ICON)
    #     # self.base_find_element(CONTACTS_CONTAINER)  # ❌ 仅检测存在性
    #     container = self.wait.until(
    #         EC.presence_of_element_located(CONTACTS_CONTAINER)
    #     )
    #     self.wait.until(
    #         lambda d: len(d.find_elements(*FRIEND_CARD)) > 0
    #     )
    #     time.sleep(1) # 等待动画效果

    def all_send_message(self,messages,target='me',phone=None, send_method='click', timeout=10):
        #判断是发消息给我还是给好友
        self.open_chat_session(target=target, phone=phone)
        time.sleep(3)
        # 原有发送逻辑
        return self.send_multiple_message(messages, send_method,timeout)

#发送媒体消息
    def send_media_messages(self,file_paths, media_type="file",target=None,phone=None,timeout=10):
        """
                发送媒体消息
                :param file_paths: 文件路径列表（支持多选）
                :param media_type: 媒体类型（file/image/video）
                :return: 是否发送成功
         """
        try:
            if target:
                self.open_chat_session(target=target, phone=phone) #根据参数发送给好友还是谁
                time.sleep(2)
            # 1. 记录发送前的最后index
            before_index = self.latest_msg_index_in_chat() or 0
            print('发送前的记录index',before_index)
            # 2. 上传文件
            self._direct_upload_files(file_paths)
            # 处理对话框弹窗
            self.handle_file_upload(timeout)

            WebDriverWait(self.driver, timeout).until(
                lambda d: (self.latest_msg_index_in_chat() or 0) > before_index
            )
            latest_index = self.latest_msg_index_in_chat()
            print('发送完成后真正的index是：',latest_index)
            if latest_index is None:
                print("未找到最新消息的 index")
                # all_messages_success = False
                return False
            try:
                success_icon = (By.CSS_SELECTOR, f"div[index='{latest_index}'] .icon-read")
                WebDriverWait(self.driver, 30).until(
                    EC.visibility_of_element_located(success_icon)
                )
                print("成功图标可见，消息发送成功")
                time.sleep(3)
            except TimeoutException:
                print("成功图标未在指定时间内出现")
            # raise AssertionError(f"消息发送失败：加载图标在 {timeout} 秒后仍然存在。错误信息: {e}")
                return False

                # 6. 验证媒体消息
            if not self.verify_media_message(media_type, file_paths, timeout):
                print("媒体验证失败")
                print('媒体信息：', media_type)
                return False

            return True

        except Exception as e:
            print(f"媒体消息发送失败: {str(e)}")
            return False

    def _direct_upload_files(self, file_paths):
        """直接操作文件输入不上传控件"""
        file_input = self.wait.until(
            EC.presence_of_element_located(FILE_INPUT)
        )
        #通过js充值input值 避免累计上一次文件
        self.driver.execute_script("""
                arguments[0].value = '';
            """, file_input)

        # 构建绝对路径（兼容Windows）
        abs_paths = [os.path.abspath(p).replace("\\", "\\\\") for p in file_paths]

        # #通过JavaScript设置文件（绕过前端限制） 这个是使隐藏的input在消息框中显示出来
        # self.driver.execute_script(f"""
        #     arguments[0].style.display = 'block';
        #     arguments[0].setAttribute('multiple', '');
        #     arguments[0].value = '';
        # """, file_input)
        # 发送文件路径（特殊字符处理）
        file_input.send_keys("\n".join(abs_paths))

    def handle_file_upload(self,timeout=30):
        try:
            dialog_confirm_button = self.base_find_element(DIALOG_FILE_CONFIRM)
            if dialog_confirm_button.is_displayed() and dialog_confirm_button.is_enabled():
                print(f"找到确认按钮: {dialog_confirm_button}")
                self.base_click(dialog_confirm_button)
            else:
                print("确认按钮不可点击")
            return True
        except Exception as e:
            print(f"弹窗处理失败: {str(e)}")
            raise

    def select_emoji_by_name(self,name):
        try:
            """通过名称选择表情"""
            emoji_loc = (By.XPATH,f"//p[text()='All Emoji']/following-sibling::article//img[contains(@src, 'emoji_{name}')]")
            # self.base_find_element(EMOJI_POPUP_SELECTOR)
            emoji =  WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable(emoji_loc))
            #滚动和悬停操作
            self.driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);",emoji)
            ActionChains(self.driver).move_to_element(emoji).pause(0.3).click().perform()
            return True
        except Exception as e:
            print(f"未找到名称为 {name} 的表情: {str(e)}")
            raise

    def _is_emoji_panel_open(self):
        """检查表情面板是否已打开"""
        try:
            return self.driver.find_element(*EMOJI_POPUP_SELECTOR).is_displayed()
        except:
            return False

    def send_emoji_message(self,emoji_names,send_method='click'):
        """发送多个表情：逐个打开面板选择"""
        self.base_click(EMOJI_ICON)
        if not self._is_emoji_panel_open():
            print('等待表情面板')
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(EMOJI_POPUP_SELECTOR)
            )
        # 逐个选择表情
        for name in emoji_names:
            if not self._is_emoji_panel_open():
                WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located(EMOJI_POPUP_SELECTOR)
                )
            self.select_emoji_by_name(name)  # 选择当前表情
            # 在选择表情后，由于面板会关闭，需要重新打开
            self.base_click(EMOJI_ICON)
            self.base_click(TEXTAREA_INPUT) # 确保输入框在选择表情后是可用的

        if send_method == 'click':
            self.send_message()
        else:
            self.send_message_via_enter()
        # 发送后等待成功图标
        latest_index = self.latest_msg_index_in_chat()
        if latest_index is  None:
            print("无法获取最新消息索引")
            return False
        success_icon = (By.CSS_SELECTOR,f"div[index='{latest_index}'] .icon-read")
        try:
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located(success_icon)
            )
            return True  # 关键修改点：成功时返回 True
        except TimeoutException:
            print("表情消息成功图标未出现")
            return False


    def verify_emoji_message(self,expected_emojis,timeout=10):
        """验证最新消息中的表情序列"""
        try:
            message_container = self.wait_for_latest_message_in_chat(timeout, 'text')
            if not message_container:
                raise Exception("未找到表情消息容器")
            # 从容器中提取表情src列表
            actual_srcs = message_container['emoji']
            print("实际表情SRC列表:", actual_srcs)
            # 验证每个预期表情名称是否存在于src中
            for name in expected_emojis:
                if not any(f'emoji_{name}' in src for src in actual_srcs):
                    print(f"未找到预期表情 '{name}'，实际SRC列表: {actual_srcs}")
                    return False
            print("所有预期表情验证成功")
            return True
            #获取当前最新文本信息内的所有表情
        except Exception as e:
            print(f"表情验证失败: {str(e)}")
            return False
#————————————————————meshchat没有语音消息
    # def send_voice_message(self,record_seconds=5):
    #     try:
    #         """发送多个表情：逐个打开面板选择"""
    #         # 定位录音按钮
    #         record_btn = self.wait.until(EC.element_to_be_clickable(VOICE_MESSAGE_BTN))
    #         # 长按录音
    #         action = ActionChains(self.driver)
    #         action.click_and_hold(record_btn)
    #         action.pause(record_seconds+1) # 增加 1 秒
    #         action.release()
    #         action.perform()
    #         print(f"✅ 成功录制 {record_seconds+1} 秒语音")
    #         # 显式等待新消息出现
    #         WebDriverWait(self.driver, 15).until(
    #             lambda d: self.latest_msg_index_in_chat() is not None
    #         )
    #         # 发送后等待成功图标
    #         latest_index = self.latest_msg_index_in_chat()
    #         if latest_index is None:
    #             print("❌ 获取最新消息索引失败")
    #             return False
    #
    #         success_icon = (By.CSS_SELECTOR, f"div[index='{latest_index}'] div.w-6.h-6 > svg")
    #         try:
    #             WebDriverWait(self.driver, 30).until(
    #                 EC.visibility_of_element_located(success_icon)
    #             )
    #             return True  # 关键修改点：成功时返回 True
    #         except TimeoutException:
    #             print("表情消息成功图标未出现")
    #             return False
    #     except Exception as e:
    #         print(f"❌ 录音操作失败: {str(e)}")
    #         return False
    #
    # def _voice_message(self,expected_duration ):
    #     try:
    #         message_container = self.wait_for_latest_message_in_chat(timeout=5, except_type='voice')
    #         if not message_container:
    #             raise Exception("未找到语音消息容器")
    #         voice_element  = message_container['latest_message_element']
    #         print("实际语音消息元素:", voice_element )
    #         duration_element = voice_element.find_element(By.CLASS_NAME, 'duration')
    #         duration_text = duration_element.text.strip()
    #         # 清洗数据：移除所有非ASCII字符
    #         cleaned_duration = ''.join([c for c in duration_text if c.isascii() and c.isdigit()])
    #         actual_duration = int(cleaned_duration)
    #
    #         print('语音时间：', actual_duration)
    #         # 允许±1秒误差
    #         is_valid = abs(actual_duration - expected_duration) <= 1
    #         print(f"✅ 时长验证 {'通过' if is_valid else '失败'} | 预期: {expected_duration}s 实际: {actual_duration}s")
    #         return is_valid,actual_duration
    #     except TimeoutException:
    #         print("⚠️ 语音消息验证超时")
    #         return False, 0
    #     except Exception as e:
    #         print(f"❌ 验证异常: {str(e)}")
    #         return False, 0

    def send_group_messages(self, messages_config, send_method='click', timeout=10):
        """专门用于群组测试的消息发送方法，不修改原有逻辑"""
        results = {}
        # 发送文本消息
        if 'text_messages' in messages_config and messages_config['text_messages']:
            texts = messages_config['text_messages']
            print(f"准备发送文本消息: {texts}")
            for text in texts:
                try:
                    self.enter_message(text)

                    if send_method == 'click':
                        self.send_message()
                    elif send_method == 'enter':
                        self.send_message_via_enter()

                    # 等待消息发送完成
                    latest_index = self.latest_msg_index_in_chat()
                    if latest_index is not None:
                        WebDriverWait(self.driver, timeout).until(
                            EC.invisibility_of_element_located(
                                (By.XPATH, f".//div[@index='{latest_index}']//i[contains(@class, 'animate-spin')]")
                            )
                        )

                    # 验证消息是否在聊天窗口中
                    if not self.is_text_message_in_chat(text):
                        print(f"警告: 文本消息 '{text}' 未在聊天窗口中找到")
                        results[f'text_{text}'] = False
                    else:
                        print(f"文本消息 '{text}' 发送成功")
                        results[f'text_{text}'] = True

                except Exception as e:
                    print(f"文本消息 '{text}' 发送失败: {e}")
                    results[f'text_{text}'] = False

        # 发送其他类型消息（使用原有方法）
        if 'image_paths' in messages_config and messages_config['image_paths']:
            image_paths = messages_config['image_paths']
            print(f"准备发送图片消息: {image_paths}")
            results['image'] = self.send_media_messages(image_paths, 'image')
            print(f"图片消息发送结果: {results['image']}")

        if 'file_paths' in messages_config and messages_config['file_paths']:
            file_paths = messages_config['file_paths']
            print(f"准备发送文件消息: {file_paths}")
            results['file'] = self.send_media_messages(file_paths, 'file')
            print(f"文件消息发送结果: {results['file']}")

        if 'video_paths' in messages_config and messages_config['video_paths']:
            video_paths = messages_config['video_paths']
            print(f"准备发送视频消息: {video_paths}")
            results['video'] = self.send_media_messages(video_paths, 'video')
            print(f"视频消息发送结果: {results['video']}")

        return results


































