# # 会话列表中查找该好友——会话列表滚动查找好友
# import time
#
# from selenium.common import NoSuchElementException
#
# from base.electron_pc_base import ElectronPCBase
#
#
# def scroll_to_element(container_locator,item_locator,target_text, max_scroll=5):
#     """
#       通用列表滚动查找方法
#       :param driver: WebDriver实例
#       :param container_locator: 滚动容器的定位器
#       :param item_locator: 列表项的定位器
#       :param target_text: 需要匹配的文本内容
#       :param max_scroll: 最大滚动次数
#       """
#     # 获取会话列表容器
#     container = base_find_element(container_locator)
#     # 当前滚动高度
#     last_position = -1
#     current_scroll = 0
#
#     while current_scroll < max_scroll:
#         # 查找当前可见的会话项
#         items = self.base_find_elements(*item_locator)
#         for item in items:
#             try:
#                 # 获取会话中的手机号
#                 # phone_element = item.find_element(*list_items_loc)
#                 if item.text.strip() == target_text:
#                     print(f"找到目标好友 {target_text}，执行点击")
#                     item.click()
#                     return True
#             except Exception as e:
#                 continue
#                 # 检查滚动位置
#         new_position = self.execute_script("return arguments[0].scrollTop", container)
#
#
#         if new_position == last_position:
#             break
#         last_position = new_position
#         current_scroll += 1
#     raise NoSuchElementException(f"未找到好友 {target_text} (已滚动 {max_scroll} 次)")
