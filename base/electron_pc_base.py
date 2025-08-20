import  json
import os
import shutil
import time
from selenium.common.exceptions import StaleElementReferenceException

from requests import options
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common import keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from  selenium.webdriver.support import  expected_conditions as EC

from pages.windows.loc.friend_locators import CARD_ITEM
from pages.windows.loc.login_locators import captcha_locator, LOGIN_SCE_DIALOG, LOGIN_AGREE
from pages.windows.loc.message_locators import TEXTAREA_INPUT, CONTACTS_ICON, CONTACTS_CONTAINER, FRIEND_CARD, \
    FRIEND_NAME, SEARCH_INPUT, SEARCH_SECTION, HOME_ICON, SESSION_LIST, FAVORITE_ICON, FAVORITE_LEFT_LIST, FAVORITE_ITEM
from utils.config_utils import ConfigUtils
from utils.logger import set_logger

from utils.captcha_solver import CaptchaSolver  # 新增导入


class ElectronPCBase:
    def __init__(self):
        config_file = os.path.join(os.path.dirname(__file__),'..', 'config_windows.json')
        self.config = ConfigUtils(config_file).read_config()
        self.electron_app_path = self.config['electron_app_path'] #读取文件内的实际app路径
        self.chromedriver_path = self.config["chromedriver_path"]
        self.logger = set_logger()
        # self.wait = WebDriverWait(driver, 10, 0.5)
        self.driver = None  # 初始化 driver 为 None
        self.wait = None  # 初始化 wait 为 None

    def start_app(self,instance_id=0):
        # 检查环境变量中是否有 chromedriver
        chromedriver_path = shutil.which("chromedriver")


        # 如果环境变量中未找到，尝试使用配置文件中的路径
        if not chromedriver_path and self.chromedriver_path:
            if os.path.exists(self.chromedriver_path):
                chromedriver_path = self.chromedriver_path
            else:
                raise FileNotFoundError(f"ChromeDriver 未找到，路径: {self.chromedriver_path}")
                # 如果仍未找到，抛出错误
            # 如果仍未找到，抛出错误
        if not chromedriver_path:
            raise EnvironmentError("ChromeDriver 未找到，请确保已将其添加到系统 PATH 环境变量中或配置文件中")

            # 配置 ChromeOptions
        options = Options()
        options.binary_location = self.electron_app_path  # 设置 Electron 应用路径
        # options.add_argument('--remote-debugging-port=9222')
        options.add_argument(f'--remote-debugging-port={9222 + instance_id}')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--user-data-dir=C:\\temp\\electron_user_data_{instance_id}')

        # 启动 ChromeDriver
        service = Service(chromedriver_path)  # 使用找到的 chromedriver 路径
        self.driver = webdriver.Chrome(service=service, options=options)

        # # 初始化 WebDriverWait
        self.wait = WebDriverWait(self.driver, 10, 0.5)
        return self.driver


    def base_find_element(self, loc):
#presence_of_element_located等待元素在dom中出现 需主注意但不一定可见如样式 display: none 不保证可被点击或者交互
        return WebDriverWait(self.driver, 10, 0.5).until(
            EC.visibility_of_element_located(loc)
        )

    def base_find_elements(self, loc):
        # 等待多个元素的可见性
        return WebDriverWait(self.driver, 10, 0.5).until(
            EC.visibility_of_all_elements_located(loc)
        )
    def base_click(self,loc):
        self.wait.until(EC.element_to_be_clickable(loc)).click()
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    def base_input_quto_text(self,loc,new_content):
        input_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(loc))

        # 清空编辑器内容（兼容富文本）
        input_element.click()
        input_element.send_keys(Keys.CONTROL + 'a')
        input_element.send_keys(Keys.BACKSPACE)
        # 添加等待确保清空完成
        WebDriverWait(self.driver, 5).until(
            lambda d: input_element.text.strip() == ""
        )
        # 输入新内容（增加显式焦点操作）
        self.driver.execute_script("arguments[0].focus();", input_element)
        ActionChains(self.driver).send_keys(new_content).perform()
    def base_input_text(self,loc,text):
        # 获取元素(找到这个元素)
        el = self.wait.until(EC.visibility_of_element_located(loc))
        # 清空操作
        # el.clear()
        el.send_keys(Keys.CONTROL+'a')
        el.send_keys(Keys.DELETE)
        print(f"已清空输入框: {loc}")
        # 输入内容
        # 使用 ActionChains 输入文本
        actions = ActionChains(self.driver)
        actions.send_keys_to_element(el, text)  # 输入文本
        actions.perform()  # 执行操作
        print(f"已通过 ActionChains 输入文本: '{text}'")
        # 获取文本值方法

    def base_get_text(self, loc):
        el = self.wait.until(EC.visibility_of_element_located(loc))
        return el.text

    def wait_for_title(self, title):
        """
        等待页面标题变为指定值
        :param title: 预期的标题
        """
        self.wait.until(EC.title_is(title))

    def base_get_text_with_js_wait(self, loc):
        # 使用 JavaScript 条件等待元素出现（支持 XPath）
        WebDriverWait(self.driver, 20).until(
            lambda d: d.execute_script(
                '''
                return document.evaluate(
                    '//div[contains(@class, "el-message--error")]//p[contains(@class, "el-message__content")]',
                    document,
                    null,
                    XPathResult.FIRST_ORDERED_NODE_TYPE,
                    null
                ).singleNodeValue !== null;
                '''
            )
        )
        # 获取元素文本
        el = self.driver.find_element(*loc)
        return el.text

#——————————————meshchat规避了验证码———————————————————
    # def is_captcha_visible(self,timeout=3):
    #     try:
    #         # 1. 先检查元素是否存在（不关心是否可见）
    #         captcha_element = self.wait.until(EC.presence_of_element_located(captcha_locator))
    #         # 2. 检查内联样式（仅适用于 style="display: none" 的情况）
    #         time.sleep(1)
    #         if not captcha_element.is_displayed():
    #             print("验证码不可见（通过is_displayed判断）")
    #             return False
    #         if "display: none" in captcha_element.get_attribute("style"):
    #             print("验证码当前不可见（通过style判断）")
    #             return False
    #         else:
    #             print("验证码可见，等待人工处理...")
    #             time.sleep(3)
    #             return True
    #     except TimeoutException:
    #         print("验证码元素不存在")
    #         return False

   #————————————————————————————————
    # def handle_captcha(self, timeout=6000):
    #     """处理拼图验证"""
    #     if self.is_captcha_visible():
    #         print("拼图验证出现，请手动完成拼图验证...")
    #         try:
    #             # 等待拼图验证元素的 display 属性变为 "none"
    #             WebDriverWait(self.driver, timeout).until(
    #                 lambda driver: driver.find_element(*captcha_locator).value_of_css_property("display") == "none")
    #             print("拼图验证已完成，继续执行后续步骤...")
    #         except TimeoutException:
    #             print("拼图验证未在指定时间内完成，继续执行后续步骤...")
    #             # 可以选择抛出异常或记录日志
    #             raise TimeoutException("拼图验证未在指定时间内完成")
    #     else:
    #         print("拼图验证未出现，跳过验证步骤，继续执行后续操作...")

    # 处理等待display的弹窗
    def close_dialog_if_exist(self, dialog_loc, close_loc):
        try:
            # 1. 首先检查元素是否存在于DOM中（无论是否可见）
            dialog_selector = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(dialog_loc))
            # 2. 然后检查元素是否可见（没有display:none）
            if dialog_selector.is_displayed():
                print("确认弹窗已出现且可见")
                self.base_click(close_loc)
                print("已确认操作")
                # 4. 等待弹窗消失
                WebDriverWait(self.driver, 3).until(
                    EC.invisibility_of_element_located(dialog_loc)
                )
            else:
                print("弹窗存在于DOM但不可见（display:none），无需处理")
        except TimeoutException:
            print("未检测到弹窗或操作超时（非关键错误）")
        except Exception as e:
            print(f"处理弹窗时出现意外错误: {e}")

    def handle_close_popup(self):
        self.close_dialog_if_exist(LOGIN_SCE_DIALOG,LOGIN_AGREE)

    def confirm_dialog(self, dialog_locator, button_locator):
        try:
            dialog = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(dialog_locator))
            if dialog:
                print("确认弹窗已出现",dialog)
            else:
                print("没有找到该弹窗",dialog)
                raise
            confirm_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(button_locator))
            if confirm_button:
                print("确认按钮已出现")
            else:
                print("没有找到确认按钮",confirm_button)
                raise
            confirm_button.click()
            print("已确认操作")
        except TimeoutException:
            print("确认弹窗操作超时，未找到元素")
        except Exception as e:
            print(f"处理二次弹窗时发生错误: {e}")

    #处理键盘事件
    def handle_keyboard_event(self,event_type,loc):
        """
        处理键盘事件
        :param event_type: 事件类型，如 'enter', 'delete', 'copy', 'paste', 'cut'
        :param element: 需要操作的元素（可选，用于复制、粘贴、剪切等操作）
        """
        element = self.driver.find_element(*loc)  # 解包元组 因为loc是(方式,loc)所以是元组需要拆开
        if event_type == 'enter':
            element.send_keys(Keys.ENTER)
        elif event_type == 'delete':
            element.send_keys(Keys.DELETE)
        else:
            raise ValueError(f"不支持键盘事件：{event_type}")

    def copy_text(self):
        """复制文本（Ctrl+C）"""
        element = self.base_find_element(TEXTAREA_INPUT)
        element.send_keys(Keys.CONTROL + 'a')  # 全选
        element.send_keys(Keys.CONTROL + 'c')  # 复制

    def paste_text(self):
        """粘贴文本（Ctrl+V）"""
        element = self.base_find_element(TEXTAREA_INPUT)
        element.send_keys(Keys.CONTROL + 'v')  # 粘贴

    def _search_friend(self,phone):
        """搜索并选择好友"""
        self.base_click(SEARCH_INPUT)
        self.base_input_text(SEARCH_INPUT,str(phone))
        self.base_find_element(SEARCH_SECTION) #等待选择框出现
        #发消息给好友-顶部搜索
        friend_select_contact_loc = (By.XPATH, f"//section[contains(@class, 'friend')]//span[contains(text(), '{phone}')]")  # 根据传入的值查找手机号
        self.base_click(friend_select_contact_loc) #到达聊天页面


    # def handle_captcha(self):
    #     """专业验证码处理流程"""
    #     if self.is_captcha_visible():
    #         print("检测到拼图验证，启动自动处理...")
    #         CaptchaSolver(self.driver).solve()
    #
    #         # 添加验证结果检查
    #         WebDriverWait(self.driver, 10).until(
    #             lambda d: 'display: none' in d.find_element(
    #                 By.CSS_SELECTOR, 'div.mask').get_attribute('style'))
    #         print("验证已通过")

    def scroll_to_element(self,
                          container_locator,
                          item_locator,
                          target_text,
                          max_scroll=5,
                          phone_locator=None,
                          raise_exception=True  # 新增参数，默认抛出异常
                          ):
        """
          通用列表滚动查找方法
          :param driver: WebDriver实例
          :param container_locator: 滚动容器的定位器
          :param item_locator: 列表项的定位器
          :param target_text: 需要匹配的文本内容
          :param max_scroll: 最大滚动次数
          """
        try:
            # 获取会话列表容器
            container = self.base_find_element(container_locator)
            # 当前滚动高度
            last_position = self.driver.execute_script(
                "return arguments[0].scrollTop", container
            )  # 初始化实际位置
            current_scroll = 0

            while current_scroll < max_scroll:
                # 查找当前可见的会话项
                items = self.base_find_elements(item_locator)
                for item in items:
                    try:
                        # 获取会话中的手机号
                        phone_element = item.find_element(*phone_locator)
                        # 空值保护 + 去空格
                        item_text = phone_element.text.strip() if phone_element.text else ""
                        if item_text == target_text:
                            print(f"找到目标好友 {target_text}，执行点击")
                            # 显式等待可点击
                            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(item)).click()
                            return True
                    except Exception as e:
                        continue
                # 滚动容器并获取最新位置
                # self.driver.execute_script(
                #     "arguments[0].scrollTop += arguments[0].offsetHeight;",
                #     container
                # ) #这是每次滚动固定高度 可能错过元素
                scroll_step = container.size["height"] * 0.3  # 每次滚动容器高度的30%
                self.driver.execute_script(
                    f"arguments[0].scrollTop += {scroll_step};",
                    container
                )
                new_position = self.driver.execute_script(
                    "return arguments[0].scrollTop", container
                )
                # 滚动位置对比
                if new_position == last_position:
                    self.logger.warning("滚动已达底部，终止循环")
                    break
                last_position = new_position
                current_scroll += 1
                # 根据参数决定是否抛出异常
                if raise_exception:
                    raise NoSuchElementException(f"未找到好友 {target_text} (已滚动 {max_scroll} 次)")
                else:
                    return False # 不抛异常，返回 False
            # raise NoSuchElementException(f"未找到好友 {target_text} (已滚动 {max_scroll} 次)")
        except Exception as e:
            print(f"滚动查找失败: {str(e)}")
            if raise_exception:
                raise
            else:
                return False  # 其他异常也返回 False
    def  open_menu_panel(self,menu_type="contacts"):
        """
            通用方法：打开不同的菜单面板
            :param menu_type:
                - "contacts": 打开联系人面板（点击CONTACTS_ICON，等待CONTACTS_CONTAINER）
                - "home": 打开主页/会话面板（点击HOME_ICON，等待SESSION_LIST）
            """
        menu_config = {
            "contacts":{
                "icon": CONTACTS_ICON,
                "left_container": CONTACTS_CONTAINER,
                "card_items": FRIEND_CARD
            },
            "home": {   
                "icon": HOME_ICON,
                "left_container": SESSION_LIST,
                "card_items": None  # 如果没有需要检查的子项可以设为None
            },
            "favorite": {
                "icon": FAVORITE_ICON,
                "left_container": FAVORITE_LEFT_LIST,
                "card_items": FAVORITE_ITEM  # 如果没有需要检查的子项可以设为None
            },


        }
        config = menu_config.get(menu_type,menu_config["contacts"]) # 获取配置 默认contacts
        self.base_click(config["icon"])
        # self.base_find_element(CONTACTS_CONTAINER)  # ❌ 仅检测存在性
        container = self.wait.until(
            EC.presence_of_element_located(config["left_container"])
        )
        if config["card_items"]:
            self.wait.until(
                lambda d: len(d.find_elements(*config["card_items"])) > 0
            )
        # time.sleep(1)  # 等待动画效果
            # 4. 替代time.sleep的智能等待（如有动画）
        self.wait.until(
            lambda d: container.value_of_css_property("opacity") == "1"
        )

    def scroll_to_friend_in_contacts(self, phone, max_scroll=5,raise_exception=True):
        """在联系人列表中滚动查找好友"""
        return self.scroll_to_element(
            CONTACTS_CONTAINER,
            FRIEND_CARD,
            phone,
            max_scroll,
            FRIEND_NAME,
            raise_exception=raise_exception)  # 传递参数)
    #切换窗口
    def switch_to_new_window_by_feature(self,feature_locator,timeout=10):
        """
                通过特征元素切换到新窗口
                :param feature_locator: 新窗口的特征元素定位器
                :param timeout: 超时时间
                :return: 新窗口句柄
                """
        main_window = self.driver.current_window_handle
        new_window = None

        def is_target_window(driver):
            nonlocal new_window
            for handle in driver.window_handles:
                if handle != main_window:
                    driver.switch_to.window(handle)
                    if len(driver.find_elements(*feature_locator)) > 0:
                        new_window = handle
                        return True
            return False

        WebDriverWait(self.driver, timeout).until(is_target_window)
        print(f"已切换到新窗口，特征: {feature_locator}, 句柄: {new_window}")
        return new_window

    def close_and_return_to_main(self, main_window, current_window=None):
        """
        关闭当前窗口并返回主窗口
        :param main_window: 主窗口句柄
        :param current_window: 要关闭的窗口句柄（None则关闭当前窗口）
        """
        if current_window:
            self.driver.switch_to.window(current_window)

        if self.driver.current_window_handle != main_window:
            self.driver.close()
            print(f"已关闭窗口: {self.driver.current_window_handle}")

        if main_window in self.driver.window_handles:
            self.driver.switch_to.window(main_window)
        elif len(self.driver.window_handles) > 0:
            self.driver.switch_to.window(self.driver.window_handles[0])
            print("主窗口已丢失，切换到第一个可用窗口")
    #封装了搜索循环用户卡片
    def find_and_click_target_card(self,card_container_loc,username_loc,userid_loc,target_phone,context_element=None):
        """
               通用卡片查找方法
               :param card_container_locator: 卡片容器定位器
               :param username_locator: 用户名字段定位器
               :param userid_locator: 用户ID字段定位器
               :param target_phone: 要查找的目标手机号
               :param context_element: 上下文元素（用于局部查找）
               """
        cards = self.base_find_elements(card_container_loc)
        if not cards:
            raise NoSuchElementException("通过搜索没有发现此用户item卡片")
        # 精准遍历逻辑
        target_card = None
        for card in cards:
            print('获取每个好友item：', card)
            if self._is_target_card(card, username_loc, userid_loc, target_phone):
                target_card = card
                break
        # 未找到时的详细错误处理
        if not target_card:
            error_info = self._collect_card_info(cards, username_loc, userid_loc)
            raise ValueError(f"未找到目标用户 {target_phone}\n可用用户信息:\n{error_info}")
        print(f'找到目标卡片：{target_phone}')
        return target_card


    def _is_target_card(self,card,username_loc,userid_loc,target):
        try:
            username = card.find_element(*username_loc).text.strip()  # 精确获取手机号元素（使用卡片作为上下文）
            print(f"当前卡片文本: [{username}] vs 目标: [{target}]")
            if userid_loc:  # 仅在 userid_loc 不为 None 时获取
                userid = card.find_element(*userid_loc).text.strip()
                return username == target or userid == target  # 如果 userid_loc 为 None，仅按用户名匹配 因为要适用分享名片用例
            return username == target
        except NoSuchElementException:
            print(f"在卡片中未找到用户名或用户ID元素")
            return False

    def _collect_card_info(self, cards, username_loc, userid_loc):
        """收集卡片信息用于错误报告"""
        info = []
        for idx, card in enumerate(cards, 1):
            try:
                name = card.find_element(*username_loc).text.strip()
                uid = card.find_element(*userid_loc).text.strip()
                info.append(f"卡片#{idx}: {name} | {uid}")
            except:
                info.append(f"卡片#{idx}: 信息不完整")
        return '\n'.join(info)

    def _get_context_element(self,latest_element,msg_type):
        """统一获取消息的右键点击区域 (供回复/转发共用)"""
        selector_map = {
            'text': '.whitespace-pre-wrap',
            'emoji': '.whitespace-pre-wrap',
            'image': '.img',
            'file': '.file',
            'video': '.video',
            'voice': '.voice',
            'card': '.card .cursor-pointer'
        }
        css_loc = selector_map.get(msg_type)
        if not css_loc:
            raise ValueError(f"不支持的消息类型: {msg_type}")
        try:
            return latest_element.find_element(By.CSS_SELECTOR, css_loc)
        except NoSuchElementException:
            raise ValueError(f"无法定位 {msg_type} 类型的消息元素")





if __name__ == "__main__":
    electron_app = ElectronPCBase()
    driver = electron_app.start_app()
    # 在这里可以添加后续操作，例如驱动浏览器等





