import time
from datetime import timedelta, datetime

from selenium.webdriver.common.by import By
from base.electron_pc_base import ElectronPCBase
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from  selenium.webdriver.support import  expected_conditions as EC

from pages.windows.loc.friend_locators import MORE_SETTING, MORE_SETTING_CONTAINER
from pages.windows.loc.group_locators import GROUP_FRIENDS_DIALOG, MEMBER_ACCOUNT
from pages.windows.loc.message_locators import SHARE_FRIENDS, SHARE_FRIENDS_DIALOG, SHARE_FRIENDS_SEARCH, \
    SHARE_FRIENDS_LEFT_CONTAINER, SHARE_FRIENDS_LEFT_ITEM, SHARE_FRIENDS_ITEM_NAME, CHECK_BUTTON, RIGHT_ITEM_CLOSE, \
    RIGHT_ITEM, RIGHT_LAST_ITEM, TARGET_FRIEND, CONFIRM_SHARE, SESSION_LIST, SESSION_ITEMS, SESSION_ITEM_UPDATES, \
    SESSION_ITEM_UPDATES_TIME, CANCEL_SHARE, HOME_ICON
from selenium.common import NoSuchElementException

class CardMessagePage(ElectronPCBase):

    def __init__(self, driver):
        super().__init__()  # 调用父类构造函数
        self.driver = driver  # 设置 driver
        self.wait = WebDriverWait(driver, 10, 0.5)

    def preare_share_friends(self,phone):
        self.open_menu_panel("contacts")
        self.scroll_to_friend_in_contacts(phone)
        print('接下来点击更多操作', MORE_SETTING)
        self.base_click(MORE_SETTING)
        self.base_find_element(MORE_SETTING_CONTAINER)
        self.base_click(SHARE_FRIENDS)

    def select_friends(self, search_queries, select_type="list",dialog_element=None):
        if dialog_element is None:
            dialog_loc = SHARE_FRIENDS_DIALOG
            username_loc = SHARE_FRIENDS_ITEM_NAME
            need_card_content = True  # 分享场景需要卡片内容
        else:
            dialog_loc = dialog_element
            username_loc = MEMBER_ACCOUNT
            need_card_content = False    # 群组场景不需要卡片内容

        self.base_find_element(dialog_loc)
        # 初始化验证容器
        expected_selected = []  # 记录实际勾选的好友标识（如用户名或手机号）
        for query in search_queries:
            if select_type == "search":
                #搜索
                self.base_click(SHARE_FRIENDS_SEARCH)
                self.base_input_text(SHARE_FRIENDS_SEARCH,query)
                time.sleep(1)
            try: # 勾选第一个匹配结果
                self.base_find_element(SHARE_FRIENDS_LEFT_CONTAINER)
                target_card = self.find_and_click_target_card(
                    card_container_loc=SHARE_FRIENDS_LEFT_ITEM,
                    username_loc= username_loc,
                    userid_loc=None,
                    target_phone=query,
                    context_element=None  # 传入窗口上下文
                ) #返回匹配的好友
                # 打印卡片HTML帮助调试
                print("完整卡片HTML:", target_card.get_attribute('outerHTML'))
                print(f'找到目标卡片：{target_card.text}')
                # 获取好友的实际显示名称
                actual_name = target_card.find_element(*username_loc).text.strip()
                expected_selected.append(actual_name)  # 保存实际名称

                check_btn = target_card.find_element(*CHECK_BUTTON)
                print("勾选框HTML:", check_btn.get_attribute('outerHTML'))
                check_btn.click()
                # 验证是否勾选成功
                is_checked = "bg-[--ms-color]" in check_btn.get_attribute("class")
                print(f"勾选框状态: {'已勾选' if is_checked else '未勾选'}")
                if not is_checked:
                    raise RuntimeError(f"勾选框状态异常，{query} 未正确勾选")

                #右侧列表即时更新
                try:
                    latest_addition = self.wait.until(
                        lambda d:d.find_element(*RIGHT_LAST_ITEM).text
                    )
                    if query not in latest_addition:
                        print(f"⚠️ 检测到显示名称差异：输入[{query}] 显示[{latest_addition}]")
                except TimeoutException:
                    raise RuntimeError("勾选后右侧列表未及时更新")

            except NoSuchElementException:
                raise RuntimeError(f"好友 {query} 的勾选框未找到")
            except Exception as e:
                raise RuntimeError(f"勾选操作失败: {str(e)}")

        selected_count =  len(self.base_find_elements(RIGHT_ITEM_CLOSE))
        print(selected_count)
        if need_card_content:
            original_content=self.get_contact_card_content()
            print('卡片内容用户：',original_content)
        else:
            original_content = "群组场景无卡片内容"  # 或者直接返回空字符串
            print('群组创建场景，跳过卡片内容获取')
        return {
            'selected_count': len(self.base_find_elements(RIGHT_ITEM_CLOSE)),
            'card_content': original_content,
            'expected_names': expected_selected  # 新增返回实际名称列表
        }
    def get_contact_card_content(self):
        element = self.base_find_element(TARGET_FRIEND)
        print('分享谁的名片：',element.text.strip())
        return element.text.strip()
    def confirm_share(self):
        self.base_click(CONFIRM_SHARE)
        # self.wait.until_not(
        #     lambda d: d.find_element(*SHARE_FRIENDS_DIALOG).is_displayed()
        # )
        self.wait.until_not(
            EC.presence_of_element_located(SHARE_FRIENDS_DIALOG)
        )
        # # 获取点击确认后的当前时间
        share_time = datetime.now().strftime("%H:%M")  # 例如 "12:30"
        print('分享好友名片的时间点：',share_time) #时间传给script方法再传递过来
        return share_time
    def cancel_share(self):
        self.base_click(CANCEL_SHARE)
        self.wait.until_not(
            lambda d: d.find_element(*SHARE_FRIENDS_DIALOG).is_displayed()
        )
        # # 获取点击确认后的当前时间
        cancel_time = datetime.now().strftime("%H:%M")  # 例如 "12:30"
        print('取消好友名片的时间点：', cancel_time)  # 时间传给script方法再传递过来
        return cancel_time

    def verify_no_share_content(self,expected_names, unexpected_content, initial_time):
        self.open_menu_panel("home")
        for name in expected_names:
            try:
                print('查看：',expected_names)
                session_item = self.find_and_click_target_card(
                    card_container_loc=SESSION_ITEMS,
                    username_loc=(By.XPATH, f".//div[contains(text(), '{name}')]"),
                    userid_loc=(By.XPATH, f".//div[contains(text(), '{name}')]"),
                    target_phone=name,
                    context_element=None
                )
                if not session_item:
                    print(f"会话 '{name}' 不存在，符合取消分享后的预期")
                    continue
                actual_content = session_item.find_element(*SESSION_ITEM_UPDATES).text
                if unexpected_content in actual_content:
                    # 如果内容匹配，检查时间戳
                    actual_time = session_item.find_element(*SESSION_ITEM_UPDATES_TIME).text
                    if actual_time == initial_time:
                        raise AssertionError(
                            f"【{name}】会话中出现了刚取消分享的名片（时间戳 {actual_time}）"
                        )
                    else:
                        print(f"⚠️ 用例失败 会话中存在历史分享记录（非本次操作），时间：{actual_time}")
                else:
                    print(f"✅ 【{name}】会话中未出现分享内容")
            except NoSuchElementException:
                print(f"✅ 【{name}】无会话记录（视为通过）")




    def verify_share_content(self,expected_names,expected_content,expected_time):
        self.open_menu_panel("home")
        #校验首页会话刚勾选的几个好友卡片中是否最新消息都是card_content的内容
        # 获取所有会话项
        sessions = self.base_find_elements(SESSION_ITEMS)
        if not sessions:
            raise NoSuchElementException("会话列表为空")

        verified_phones = []  # 通过记录已验证的电话号码，可以清楚地知道哪些验证成功，哪些失败。
        # unique_names = list(set(expected_names))  # 去重
        for name in expected_names:
            try:
                print(f"正在查找用户: {name}")  # 增加调试信息
                session_item = self.find_and_click_target_card(
                    card_container_loc= SESSION_ITEMS,
                    username_loc=(By.XPATH, f".//div[contains(text(), '{name}')]"),
                    userid_loc=(By.XPATH, f".//div[contains(text(), '{name}')]"),
                    target_phone=name,
                    context_element=None
                )
                if session_item:
                    print('找到该用户元素了', session_item.text)
                else:
                    print('未找到该用户')
                #获取卡片的最新内容
                actual_content_element = session_item.find_element(*SESSION_ITEM_UPDATES)
                actual_content = actual_content_element.text  # 获取最新消息文本内容
                #获取卡片的最新消息中的时间点
                actual_time_element = session_item.find_element(*SESSION_ITEM_UPDATES_TIME)
                actual_time = actual_time_element.text
                print(f"实际完整内容2：{actual_content}")
                print(f"传过来的用户text：{expected_content}")
                if isinstance(expected_content, list): #以防是列表['数据']
                    expected_content = expected_content[0]  # 取第一个元素

                if expected_content not in actual_content:
                    raise  AssertionError(f"内容不匹配\n预期包含: {expected_content}\n实际内容: {actual_content.text}")
                # 验证时间
                # actual_time = datetime.strptime(actual_time_str, "%H:%M")  # 若显示为 12:30 格式
                assert actual_time == expected_time, f"时间不匹配: 预期 {expected_time}，实际 {actual_time}"
                verified_phones.append(name)

            except Exception as e:
                print(f"验证 {name} 失败: {str(e)}")
                continue
        #最终结果检查 注意一定放在循环外面！
        unverified = set(expected_names) - set(verified_phones)
        assert not unverified, f"未验证的会话: {unverified}"

    def clear_all_selected_friends(self):
        initial_count = len(self.base_find_elements(RIGHT_ITEM))
        print(f"初始已选数量: {initial_count}")
        # 逐个点击关闭按钮 遍历清除所有选项
        for i in range(initial_count):
            try:
                last_item = self.base_find_element(RIGHT_LAST_ITEM)
                # 记录即将清除的用户信息
                user_name = last_item.find_element(*SHARE_FRIENDS_ITEM_NAME).text
                print(f"🚀 正在清除第{i+1}个用户: {user_name}")
                # 执行清除操作
                close_btn = last_item.find_element(*RIGHT_ITEM_CLOSE)
                close_btn.click()
                # 验证左侧状态
                checked = self.is_friend_checked(user_name)
                assert not checked, f"{user_name} 左侧的勾选状态未正确清除"
            except NoSuchElementException:
                break  # 如果找不到项则终止循环
        # # 最终状态验证
        # self._verify_final_state()
        # time.sleep(2)
        # self.base_click(CANCEL_SHARE)
        # self.base_click(HOME_ICON)

    def _verify_final_state(self):
        # 验证确认按钮状态
        confirm_btn = self.base_find_element(CONFIRM_SHARE)
        assert not confirm_btn.is_enabled(), "清空后确认按钮应处于禁用状态"
        self.base_click(CANCEL_SHARE)
        self.base_click(HOME_ICON)



    def is_friend_checked(self,friend_name):
        try:
            # 找到左侧好友列表中对应的好友卡片
            friend_card = self.wait.until(
                lambda d: d.find_element(By.XPATH,
                f"//div[contains(@class, 'left')]//article[contains(., '{friend_name}')]")
            )
            # 查找勾选框
            check_button = friend_card.find_element(*CHECK_BUTTON)
            # 检查勾选状态
            return "bg-[--ms-color]" in check_button.get_attribute("class")
        except NoSuchElementException:
            return False  # 如果找不到该好友，返回未勾选


