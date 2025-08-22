import time

from base.electron_pc_base import ElectronPCBase
from selenium.webdriver.support.wait import WebDriverWait
from  selenium.webdriver.support import  expected_conditions as EC
from pages.windows.card_message_page import CardMessagePage
from pages.windows.friend_operation_page import FriendOperationPage
from pages.windows.loc.message_locators import ICON_MORE, MORE_PAN, BLOCK_BUTTON, UNBLOCK_BUTTON, CONFIRM_REQUEST, \
    CANCEL_SHARE
from pages.windows.message_text_page import MessageTextPage


class BlockMessagePage(ElectronPCBase):

    def __init__(self, driver):
        super().__init__()  # 调用父类构造函数
        self.driver = driver  # 设置 driver
        self.wait = WebDriverWait(driver, 10, 0.5)
        self.msg_page = MessageTextPage(driver)  # 复用消息发送功能
        self.card_page = CardMessagePage(self.driver)  # 直接复用已有页面对象


    def is_blocked(self):
        """
       判断当前是否已拉黑好友：
       - 如果页面有 'Unblock' 按钮 → 已拉黑 → 返回 True
       - 如果页面有 'Block' 按钮 → 未拉黑 → 返回 False
       """
        try:
            self.wait.until(EC.visibility_of_element_located(UNBLOCK_BUTTON))
            print('当前状态已拉黑，找到unblock')
            return True  # 已拉黑
        except:
            try:
                self.wait.until(EC.visibility_of_element_located(BLOCK_BUTTON))
                print('当前状态未拉黑，找到block')
                return False # 未拉黑
            except:
                raise Exception("未找到 'Block' 或 'Unblock' 按钮，请确认在单聊页面")

    def verify_message_not_received(self, message):
        try:
            # 使用现有的方法检查消息
            result = self.msg_page.is_text_message_in_chat(message, timeout=10)  # 缩短超时时间

            # 如果返回True，说明消息存在，这是不应该的
            if result:
                print(f"错误: 收到了不应该收到的消息: {message}")
                return False
            else:
                print(f"验证成功: 未收到消息: {message}")
                return True

        except Exception as e:
            # 如果超时或其他异常，通常意味着消息不存在
            print(f"消息验证完成（预期消息不存在）: {e}")
            return True

    def verify_message_block(self,instance_manager,receiver_account,action_type,expected_result,sender):
        print(f"\n=== 开始消息验证: {action_type}操作后{expected_result} ===")
        # 获取当前用户信息（发送者）
        print(f"\n=== 启动receiver实例 原本账号：{sender}===")
        receiver_driver= instance_manager.start_receiver_instance(receiver_account)
        receiver_page = BlockMessagePage(receiver_driver)
        receiver_page.msg_page.open_chat_session('friend', sender)  # 打开每个勾选的单聊页面
        # 接收者发送消息
        receiver_page.msg_page.send_multiple_message(expected_result,'click')
        # 短暂等待消息传输
        time.sleep(3)
        # 切换回主driver验证消息
        self.driver.switch_to.window(self.driver.current_window_handle)
        self.msg_page.open_chat_session('friend', receiver_account['username'])  # 打开每个勾选的单聊页面

        if action_type=='cancel':
            result = self.msg_page.is_text_message_in_chat(expected_result[0])
            if result:
                print("✓ 验证成功: 正常收到消息")
            else:
                raise AssertionError(f"应该收到消息 '{expected_result[0]}' 但未收到")
        elif action_type=='block':
            result = self.verify_message_not_received(expected_result[0])
            if result:
                print("✓ 验证成功: 拉黑后未收到消息")
            else:
                raise AssertionError(f"拉黑后不应该收到消息 '{expected_result[0]}'，但收到了")
        elif action_type=='unblock':
            time.sleep(2)
            result = self.msg_page.is_text_message_in_chat(expected_result[0])
            if result:
                print("✓ 验证成功: 正常收到消息")
            else:
                raise AssertionError(f"应该收到消息 '{expected_result[0]}' 但未收到")




    def block_friend(self,target,phone,actions,instance_manager,receiver_account,sender):
        self.msg_page.open_chat_session(target, phone)  # 打开每个勾选的单聊页面
        self.base_click(ICON_MORE)
        self.wait.until(EC.visibility_of_element_located(MORE_PAN))
        for action in actions:
            print(f"=== 执行操作: {action} ===")
            #每次操作前重新获取状态
            current_status = self.is_blocked()
            if action == 'cancel':
                if not current_status:
                    self.base_click(BLOCK_BUTTON)
                    #先取消拉黑
                    self.base_click(CANCEL_SHARE)
                    self.wait.until(EC.visibility_of_element_located(BLOCK_BUTTON))
                    assert self.is_blocked() == False,'取消拉黑验证失败，错误触发拉黑按钮'
                    print('执行取消拉黑完成')
                    msg = ["取消拉黑--应该能收到消息"]
                    self.verify_message_block(instance_manager,
                                              receiver_account,
                                              'cancel',
                                              msg,
                                              sender)
                else:
                    print('----当前已是拉黑状态，无需执行取消操作')

            elif action == 'block':
                if not current_status:
                    self.base_click(BLOCK_BUTTON)
                    self.base_click(CONFIRM_REQUEST)
                    self.wait.until(EC.visibility_of_element_located(UNBLOCK_BUTTON))
                    assert self.is_blocked() == True, '拉黑状态失败，状态未改变'
                    print('执行拉黑 完成')
                    msg = ["执行拉黑--不应该收到消息"]
                    self.verify_message_block(instance_manager,
                                              receiver_account,
                                              'block',
                                              msg,
                                              sender)
                else:
                    print('----当前已是拉黑状态，无需执行拉黑操作')
            elif action == 'unblock':
                if current_status:
                    time.sleep(1)
                    self.base_click(UNBLOCK_BUTTON)
                    self.wait.until(EC.visibility_of_element_located(BLOCK_BUTTON))
                    assert self.is_blocked() == False, '取消拉黑状态失败，状态未改变'
                    print('执行 解除拉黑 完成 ')
                    time.sleep(1)
                    msg = ["解除·拉黑--应该收到消息"]
                    self.verify_message_block(instance_manager,
                                              receiver_account,
                                              'unblock',
                                              msg,
                                              sender)
                else:
                    print('----当前已是未拉黑状态，无需执行解除操作')




