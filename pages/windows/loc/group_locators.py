from selenium.webdriver.common.by import By

CROUP_CHAT = (By.XPATH,"//span[text()='Create Group Chat']")
CROUP_NAME_DIALOG = (By.XPATH,"//div[@role='dialog' and contains(., 'Create Group Chat')]")
CROUP_NAME_INPUT = (By.CSS_SELECTOR,"input.el-input__inner[placeholder='Group Chat Name']")
SELECT_MEMBERS_DIALOG = (By.CSS_SELECTOR, ".el-dialog__body > article.box")
GROUP_DIALOG_CONFIRM = (By.XPATH,"/html/body/div[1]/main[2]/article/main/article[1]/section/aside/div/div[2]/div/div/div/article/article[2]/button[2]/span")

GROUP_FRIENDS_DIALOG = (By.XPATH,"//div[@role='dialog' and contains(., 'Create Group Chat')]")
MEMBER_ACCOUNT = (By.CSS_SELECTOR,"article.card .name")
MEMBER_NUMBER = (By.XPATH,"//*[@id='chat-header']/section/div/p[2]")
SUCCESS_GROUP_TIP = (By.CSS_SELECTOR,".group-invite")
BREAK_GROUP = (By.XPATH,"//section[@class='del cursor-pointer box-item' and text()='Break up the group chat']")
CONTEXT_MENU_DELETE = (By.XPATH, "//div[contains(@class, 'mx-context-menu-item')]//span[text()='Delete']")
GROUP_FOOTER_MESSAGE = (By.CSS_SELECTOR, "footer.footer p")
CLEAR_CONTAINER =(By.CSS_SELECTOR,".mx-context-menu[data-type='ContextSubMenu']")
DIALOG_CONFIRM = (By.XPATH,"//div[@role='dialog']//button[span[text()='Confirm']]")