# 获取所有卡片（带异常处理）
cards = self.base_find_elements(CARD_ITEM)
if not cards:
    raise NoSuchElementException("通过搜索没有发现此用户item卡片")
# 精准遍历逻辑
target_card = None
for card in cards:
    try:
        username_element = card.find_element(*USERNAME_IN_CARD)  # 精确获取手机号元素（使用卡片作为上下文）
        current_username = username_element.text.strip()
        # 带格式清理的对比（处理可能的特殊字符）
        if current_username == phone:
            target_card = card
            break
        userid_element = card.find_element(*USERNAME_IN_ID)
        current_userid = userid_element.text.strip()
        if current_userid == phone:  # 假设phone可能为用户ID
            target_card = card
            break
    except NoSuchElementException:
        continue

    # 带详细日志的异常处理
if not target_card:
    # 收集所有卡片的用户名和用户ID用于错误提示
    available_users = []
    for c in cards:
        try:
            name = c.find_element(*USERNAME_IN_CARD).text.strip()
            userid = c.find_element(*USERNAME_IN_ID).text.strip()
            available_users.append(f"用户名: {name} | ID: {userid}")
        except NoSuchElementException:
            available_users.append("元素缺失")
    raise ValueError(
        f"目标手机号 {phone} not found in results. Available: {available_users}"
    )