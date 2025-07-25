from selenium.webdriver.common.by import By
#个人头像
MY_AVATAR =(By.XPATH,'//*[@id="app"]/main[2]/aside/article[1]')
AVATAR_MENU=(By.XPATH,'//*[@id="app"]/main[2]/aside/main')
AVATAR_MESSAGE_Button=(By.XPATH,'//*[@id="app"]/main[2]/aside/main/article[2]/div[2]/span')
#输入文本内容
TEXTAREA_INPUT = (By.XPATH,"//div[contains(@id, 'w-e-textarea')]")
TEXTAREA_INPUT2 = (By.CSS_SELECTOR, "div.editor-content[data-w-e-textarea] > div.w-e-text-container [contenteditable='true']")
Message_Send = (By.XPATH,"//footer//button[contains(@class,'el-button')]") #发消息按钮
#登入后的手机号
PHONE_LOC = (By.CSS_SELECTOR,'.name.line-clamp-2.select-text')
# CURRENT_WINDOW_PHONE=(By.XPATH,'//article[@class="header"]//p[@class="truncate"]')
CURRENT_WINDOW_PHONE=(By.XPATH,"//article[@class='header']//div[@class='header-title-left no-select no-drag']/p[@class='truncate' or contains(@class, 'max-w')]")

#检查单聊中是否存在该消息
CHAT_MESSAGE = (By.XPATH,'#chat-message') #聊天窗口
ALL_TEXT = (By.CSS_SELECTOR,".whitespace-pre-wrap")
ALL_MESSAGE = (By.CSS_SELECTOR,".chat-message div[index]") #验证消息加载消失表示发送成功

#右键菜单
MENU_ITEMS = {
    'select_all': (By.XPATH, "//div[contains(@class, 'mx-context-menu-item')]//span[contains(text(), 'Select All')]"),
    'paste': (By.XPATH, "//div[contains(@class, 'mx-context-menu-item')]//span[contains(text(), 'Paste')]"),
    'cut': (By.XPATH, "//div[contains(@class, 'mx-context-menu-item')]//span[contains(text(), 'Cut')]"),
    'copy': (By.XPATH, "//div[contains(@class, 'mx-context-menu-item')]//span[contains(text(), 'Copy')]")
}
#发消息给好友-顶部搜索账号
SEARCH_INPUT =(By.CSS_SELECTOR,"input.el-input__inner[placeholder='Search']")
SEARCH_SECTION = (By.CSS_SELECTOR,".el-scrollbar.searchInfo.no-select") #弹窗出现

#发消息给好友 -回话列表中查找
SESSION_LIST = (By.CSS_SELECTOR,"article.flex-1.overflow-y-auto") # 会话列表容器
SESSION_ITEMS = (By.CSS_SELECTOR,"div.no-select.item") #单个会话项
SESSION_PHONE = (By.CSS_SELECTOR, ".item-content-header-title .truncate")  # 会话中的手机号

#发消息给好友 -从联系人中查找该好友
CONTACTS_ICON =(By.CSS_SELECTOR, "article.tool-icons > section:nth-child(2)") # 侧边栏菜单
# CONTACTS_CONTAINER =(By.CLASS_NAME,"el-scrollbar__view")  # 联系人容器
CONTACTS_CONTAINER =(By.CSS_SELECTOR,".no-select.content")
FRIEND_BUTTON=(By.CLASS_NAME, "tabs-box-item text-[--ms-color]")
FRIEND_SECTION = (By.CSS_SELECTOR,".friend") # 好友分组区块
FRIEND_CARD = (By.CLASS_NAME, "friend-card")  # 单个好友卡片
FRIEND_NAME = (By.CSS_SELECTOR,".friend-card .name") # 好友名称
SEND_MSG_BUTTON =(By.XPATH,"//div[contains(text(), 'Send Message')]")

#发送多媒体消息
UPLOAD_FILE =(By.CSS_SELECTOR, "i.icon-file") #媒体第一个文件图标
FILE_INPUT = (By.CSS_SELECTOR, "input[type='file']") #隐藏的input总体上传所有媒体的loc
# DIALOG_FILE =(By.CSS_SELECTOR, "//div[contains(@class, 'el-overlay-dialog')]//div[contains(text(), 'Send To')]") #注意中文状态下不可用
DIALOG_FILE =(By.CSS_SELECTOR, "//div[contains(@class,'el-dialog__body') and .//*[contains(text(),'Send To')]]") #注意中文状态下不可用
DIALOG_FILE_CONFIRM = (By.XPATH,"/html/body/div[1]/main[2]/article/main/article/main/div[2]/div/div/div/section/button[2]/span")
# DIALOG_FILE_CONFIRM = (By.CSS_SELECTOR,"//div[@role='dialog']//button[span[text()='Confirm']]")

#确认媒体消息出现在单聊ui上面
MESSAGE_CONTAINER = (By.CSS_SELECTOR, ".chat-item-box") # 所有消息的公共父容器
FILE_CONTAINER = (By.CSS_SELECTOR, ".chat-item-box .chat-item-content .file") #文件容器
FILE_NAME = (By.CSS_SELECTOR, ".file-name") #文件名称
# VIDEO_CONTAINER= (By.CSS_SELECTOR,".chat-item-box .chat-item-content .video")
VIDEO_CONTAINER= (By.CSS_SELECTOR,".video")
# IMAGE_CONTAINER= (By.CSS_SELECTOR,".chat-item-box .chat-item-content .img")
IMAGE_CONTAINER= (By.CSS_SELECTOR,".img")

#发送表情消息
EMOJI_ICON = (By.CSS_SELECTOR, ".icon-emoji") # 表情自定义图标
# EMOJI_POPUP_SELECTOR = (By.CSS_SELECTOR,'div.el-popper[role="tooltip"]')  # 表情弹框容器
EMOJI_POPUP_SELECTOR = (By.CSS_SELECTOR,'div.el-popper[role="tooltip"] main article:nth-of-type(2)')  # 表情弹框容器
EMOJI_ICON_SELECTOR = (By.CSS_SELECTOR,'article[data-v-43a55c74] section > section img')  # 所有表情

#语音消息
VOICE_MESSAGE_BTN = (By.CSS_SELECTOR,'.icon-recording')
VOICE_MESSAGE_CONTAINER = (By.CSS_SELECTOR,'.chat-item-content .voice')

#名片消息
SHARE_FRIENDS = (By.XPATH,"//div[contains(@class, 'mx-context-menu')]//span[text()='Share with friends']")
SHARE_FRIENDS_DIALOG =(By.XPATH,"//div[@role='dialog' and contains(., 'Send To')]")
SHARE_FRIENDS_SEARCH = (By.XPATH,"//div[contains(@class, 'el-overlay-dialog')]//input[@placeholder='Search']")
SHARE_FRIENDS_LEFT_CONTAINER = (By.XPATH,"//div[contains(@class, 'dialog')]//div[@class='left']//article[@class='content']")
SHARE_FRIENDS_RIGHT_CONTAINER = (By.XPATH,"//div[contains(@class, 'dialog')]//div[contains(@class, 'content')]") #勾选列表
SHARE_FRIENDS_LEFT_ITEM = (By.XPATH,"//div[contains(@class, 'dialog')]//article[@class='card']") #每个好友卡片
SHARE_FRIENDS_ITEM_NAME = (By.XPATH,".//p[@class='truncate']")
CHECK_BUTTON = (By.XPATH,"./div[contains(@class, 'check')]")
RIGHT_ITEM = (By.XPATH,"//div[contains(@class, 'right')]//div[contains(@class, 'card')]") #每个被勾选的好友卡片
RIGHT_LAST_ITEM = (By.XPATH,"//div[contains(@class, 'right')]//div[contains(@class, 'card')][last()]") #右侧最后一个item
RIGHT_ITEM_CLOSE = (By.XPATH,".//div[contains(@class, 'close')]//i")
TARGET_FRIEND = (By.XPATH,"//article[contains(@class, 'px-5')]//div[contains(@class, 'text-[#757575]')]")
SESSION_ITEM_UPDATES = (By.CSS_SELECTOR,".item-content-message-content")#通过SESSION_ITEMS 识别最新消息
SESSION_ITEM_UPDATES_TIME = (By.CSS_SELECTOR,".item-content-header-date") #识别最新消息的时间点
#对话框按钮
CONFIRM_SHARE = (By.XPATH,"//article[@class='footer']//button[.//span[text()='Confirm']]")
CONFIRM_DISABLED = (By.XPATH, "//button[contains(@class, 'is-disabled')]//span[text()='Confirm']") # 确认按钮禁用状态
CANCEL_SHARE = (By.XPATH,".//span[text()='Cancel']")
HOME_ICON = (By.CSS_SELECTOR,"article.tool-icons > section:nth-child(1)")

#————————消息操作
#消息引用
MSG_ACTIONS_REPLY = (By.XPATH,".//span[text()='Reply']")
QUOTE_BOX = (By.XPATH,"//article[contains(@class, 'quote-box')]")
QUOTE_BOX_USER = (By.XPATH,"//div[@class='flex-shrink-0']")#可通QUOTE_BOX去找USER
QUOTE_BOX_MSG = (By.XPATH,"//article[contains(@class, 'truncate')]")#可通QUOTE_BOX去找MSG
QUOTE_BOX_CLOSE = (By.XPATH,"//article[contains(@class, 'quote-box')]//i[contains(@class, 'icon-close')]")

CHAT_QUOTE_MSG2_BE_CITE_TXT = (By.CSS_SELECTOR,'.quote-box .break-all')# chat中的上面被引用部分 到时通过wait返回的元素去查找这个
CHAT_QUOTE_FILE = (By.CSS_SELECTOR, ".file-info .name") # 文件名
CHAT_QUOTE_IMAGE = (By.CSS_SELECTOR, ".image-thumbnail") # 图片缩略图
CHAT_QUOTE_VIDEO = (By.CSS_SELECTOR, ".video-thumbnail") # 视频缩略图
CHAT_QUOTE_VOICE = (By.CSS_SELECTOR, ".voice-duration") # 语音时长

CHAT_QUOTE_MSG_CITE = (By.CSS_SELECTOR, ".cite-text")  # chat中的下面引用部分 到时通过wait返回的元素去查找这
CHAT_QUOTE_MSG_USER = (By.CSS_SELECTOR,".text-sm") # chat中的用户 到时通过wait返回的元素去查找这
#消息引用-媒体类型
CHAT_FILE_NAME = (By.CSS_SELECTOR,".cite .line-clamp-2") #文件名称
#图片 div[index='41'] .chat-item-box .chat-item-content .cite img 可得到 必须配合index否则所有缩略图都
CHAT_QUOTE_IMG_TH = (By.CSS_SELECTOR,".img")
CHAT_QUOTE_IMG_MP4 = (By.CSS_SELECTOR,".chat-item-box .chat-item-content .cite")
# CHAT_QUOTE_VOICE_TH = (By.CSS_SELECTOR,".icon-voice")

#————————消息转发
MSG_ACTIONS_FORWARD = (By.XPATH,".//span[text()='Forward']")
# 消息状态图标
# MSG_READ_STATUS = (By.CSS_SELECTOR, ".icon-read[src*='read-none']")  # 根据实际图片路径调整
MSG_READ_STATUS = (By.CSS_SELECTOR, ".icon-read")
# 成功状态标识列表（发送成功、已读均视为成功）
SUCCESS_STATUS_FLAGS = ["read-none", "read-over"]

#——————————消息选择
MSG_ACTIONS_SELECT = (By.XPATH,".//span[text()='Select']")
CHECK_ELEMENT = (By.CSS_SELECTOR,"article.chat-item.items-center.isMe > div.check")
SELECT_FORWARD = (By.CSS_SELECTOR,'article.redirection-item:nth-child(1)')
SELECT_DELETE = (By.CSS_SELECTOR,'article.redirection-item:nth-child(2)')
SELECT_CLOSE = (By.CSS_SELECTOR,'footer.redirection > article:nth-child(3)')
MESSAGE_ITEM = (By.CSS_SELECTOR,"")
CHAT_TIME = (By.CSS_SELECTOR,"div.chat-item-box span.opacity-50")
CONFIRM_SELECT_DELETE = (By.CSS_SELECTOR,".el-dialog__body .el-button--primary")

#——————————消息删除
MSG_ACTIONS_DELETE = (By.XPATH,".//span[text()='Delete']")
#——————————消息撤回
MSG_ACTIONS_RECALL = (By.XPATH,".//span[text()='Recall']")
#——————————消息编辑
MSG_ACTIONS_EDIT = (By.XPATH,".//span[text()='Edit']")
EDIT_TIP = (By.CSS_SELECTOR,".text-red-500")

#——————————消息复制
MSG_ACTIONS_COPY = (By.XPATH,".//span[text()='Copy']")
#————————删除好友请求数据
DELETE_ICON = (By.CSS_SELECTOR,".header-right > i")
LEFT_NEW_FRIEND = (By.XPATH,".//div[@class='card-left'][text()='New Friends']")
RIGHT_NEW_FRIEND_CONTAINER = (By.XPATH, ".//main[@class='new-friend']")
FRIEND_REQUEST_LIST  = (By.CSS_SELECTOR, ".newFriend .el-scrollbar__view > div")
CONFIRM_REQUEST = (By.XPATH, "//div[contains(@class, 'el-dialog__body')]//button[span[text()='Confirm']]")
#————————————单钩双钩
double_check_icon = "div[index='{index}'] div > svg path:nth-of-type(2)"

# 单勾选择器 (只有1个path)
single_check_icon = "div[index='{index}'] div > svg path:only-of-type"

#————————————同意好友请求
ACCEPT_FRIEND_ITEM = (By.CSS_SELECTOR,"article.item.no-select")
FRIEND_ACCOUNT = (By.CSS_SELECTOR,".content > div:first-child > span")
REJECT_BUTTON = (By.CSS_SELECTOR,"button.el-button--small:nth-of-type(1)")
ACCEPT_BUTTON = (By.CSS_SELECTOR,"button.el-button--primary.el-button--small")
ACTION_RESULT_TEXT = (By.CSS_SELECTOR,".right > :last-child")

