from selenium.webdriver.common.by import By
MORE_SETTING=(By.CSS_SELECTOR,'.el-icon.more') #...
MORE_SETTING_CONTAINER =(By.XPATH,"//div[contains(@class, 'mx-context-menu') and contains(@class, 'light') and contains(@class, 'mx-menu-host')]") #动弹menu
DELETE_CONTACT = (By.XPATH,"//div[contains(@class, 'mx-context-menu')]//span[text()='Delete Contact']") #menuitem 删除
CONFIRM_DIALOG_DELETE = (By.XPATH, "//div[@class='el-overlay no-drag']//div[@role='dialog' and contains(@class, 'el-overlay-dialog') and .//div[contains(text(), 'Delete Contact')]]")
CONFIRM_BUTTON = (By.XPATH, "//div[@role='dialog']//button[contains(@class, 'el-button--primary') and contains(., 'Confirm')]")

#加好友—— +菜单栏添加
CREATE_MENU_BUTTON = (By.XPATH,"//div[@class='no-drag add cursor-pointer']")
CREATE_MENU_CONTAINER = (By.XPATH,"//div[@class='mx-context-menu  light mx-menu-host']")
ADD_FRIEND_ITEM = (By.XPATH,"//span[text()='Add Friend']")
APPLICATION_FRIEND = (By.XPATH,"//main[contains(@class, 'add-friend')]")  #点击添加好友后的申请界面
SEARCH_FRIEND = (By.XPATH,"//input[@placeholder='Enter Phone Number / SecureNet ID']")
SEARCH_BUTTON = (By.XPATH,"//button[span[text()='Search']]")
CARD_ITEM = (By.CSS_SELECTOR, "article.card-item")  # 更稳定的CSS选择器#每个card 后面通过这个card去找名字
USERNAME_IN_CARD = (By.CSS_SELECTOR, ".base .name")  # 手机号专属元素
USERNAME_IN_ID = (By.CSS_SELECTOR, ".base .id")
# ADD_BUTTON = (By.XPATH,"//button[span[text()='Add']]")
ADD_BUTTON_IN_CARD = (By.XPATH, ".//button[span='Add']")  # 相对定位

#加好友—— 顶部搜索添加
HEADER_ADD_FRIEND = (By.XPATH,"//section[contains(@class, 'header-add-friend')]")
FRIEND_CARD_ITEM = (By. XPATH, "//section[@class='friend']//article[@class='item']")
FRIEND_NAME_IN_CARD = (By.XPATH, ".//section/p[1]")  # 第一个<p>标签是用户名
FRIEND_ID_IN_CARD = (By.XPATH, ".//section/p[2]/span")  # 第二个<p>标签内的<span>是ID

#加好友——共用loc
SEND_FRIEND_REQUEST_CONTAINER = (By.XPATH,"//main[contains(@class, 'apply-friend')]")
SEND_REQUEST_BUTTON = (By.XPATH,"//button[span[text()='Send']]")
REQUEST_SUCCEED = (By.XPATH,"//div[contains(@class, 'el-message--success')]//p[contains(text(), 'Request Sent')]")
#关闭对话框窗口
CLOSE_BUTTON = (By.CSS_SELECTOR,'.add-friend  i.iconfont.icon-close')
#验证发送申请请求好友后
