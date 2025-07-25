from selenium.webdriver.common.by import By

LOGO_ACCOUNT_LOGIN=(By.XPATH,"//div[@class='group login-type']//img[@class='group-hover:hidden login-type-icon'][1]")
USERNAME_INPUT = (By.XPATH, '/html/body/div[1]/div/div[1]/section/div/article/form/div[1]/div/div/div/input')
PASSWORD_INPUT = (By.XPATH, '/html/body/div[1]/div/div[1]/section/div/article/form/div[2]/div/div/div/input')
COMBOBOX_DROPDOWN1 = (By.XPATH,'/html/body/div[1]/div/div[1]/section/div/article/form/div[3]/div/div/div/div[1]/div[2]')
COMBOBOX_DROPDOWN2 = (By.XPATH,'//*[@id="app"]/div/div[1]/section/div/article/form/div[4]/div/div/div/div[1]/div[2]')
LOCAL =  (By.XPATH,"//span[text()='Local']")
FIRM = (By.XPATH,"//span[text()='MESH']")
AD_LOGIN =  (By.XPATH,"//span[text()='AD Login']")
TERM = (By.XPATH,'//*[@id="app"]/div/div[1]/section/div/article/div[1]/label/span')
# TERM = (By.XPATH,'//*[@id="app"]/div/div[1]/section/div/article/div[1]/label/span')
# REMEMBER= (By.CSS_SELECTOR,".el-checkbox__label")
REMEMBER= (By.XPATH,'//*[@id="app"]/div/div[1]/section/div/article/form/div[4]/div/section/label/span[1]')

LOGIN_BUTTON = (By.XPATH, "//button[span[text()='Login']]")
# ERROR_MESSAGE = (By.CSS_SELECTOR, ".error-message")
OK = (By.XPATH, "/html/body/div[3]/div/div/div[3]/button[2]")

# ERROR_ALERT=(By.CSS_SELECTOR,"#message_1 .el-message__content")
# 或者 //div[contains(@class, 'el-message--error')]//p
#或者 div.el-message.el-message--error > p.el-message__content
ERROR_ALERT=(By.XPATH,"//div[contains(@class, 'el-message--error')]//p[contains(@class, 'el-message__content')]")
PHONE_ERROR_TIP =(By.XPATH,'//*[@id="app"]/div/div[1]/section/div/article/form/div[1]/div/div[2]')
PASSWORD_ERROR_TIP= (By.XPATH,'//*[@id="app"]/div/div[1]/section/div/article/form/div[2]/div/div[2]')

# captcha_locator = (By.XPATH, '//*[@id="app"]/div/div[1]/section/div/article/div[2]')  # 替换为实际的选择器
captcha_locator = (By.CSS_SELECTOR, 'div.mask')  # 替换为实际的选择器

# LOGIN_SCE_DIALOG=(By.XPATH,'//*[@id="app"]/div[1]/div/div')
LOGIN_SCE_DIALOG=(By.XPATH,'//*[@id="app"]/div[1]')
LOGIN_AGREE =  (By.XPATH,"//span[text()='Agree']")
LOGIN_CLOSE = (By.XPATH,'//*[@id="app"]/div[1]/div/div/footer/article/button[2]')

