# 安装对应app内置chrome对应版本的chrome驱动器 控制台输入navigator.userAgent 查看
# Chrome/124.0.6367.243 这是app暂时版本
# 安装环境
pip install -r requirements.txt
# 前提账号关系准备 主账号+三个账号好友关系 2留着非好友关系

result = self.card_page.select_friends(search_queries=search_queries,select_type=select_type)
    #由于文本和媒体需是列表形势需要的是[0]但是表情不需要 所以做个声明
    processed_content = message_content[0] if media_type != "emoji" and isinstance(message_content,list) else message_content
    # 3. 根据操作类型处理
    if operation_type == "confirm":
        share_time = self.card_page.confirm_share()
        self._verify_forward_result(
            expected_names=result['expected_names'],
            expected_content=processed_content,  # 使用处理后的内容
            expected_time=share_time,
            media_type=media_type
        )


























