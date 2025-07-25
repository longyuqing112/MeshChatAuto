import redis
from pymongo import MongoClient

class DatabaseConnection:
    def connect_mongodb(self, username):
        """ 连接 MongoDB 并插入登录日志 """
        try:
            uri = "mongodb://root:YweICq7E4svoWm@192.168.3.171:27017"

            client = MongoClient(uri)  # 连接到本地 MongoDB
            client.admin.command('ping')  # 试图连接到数据库
            print("连接成功！")
            db = client["user"]  # 选择数据库
            collection = db["user_info"]  # 选择集合

            query = {"nameName": username}
            # 查询用户名是否在数据库里面  如果不在报错
            # result = collection.find_one(query)
            result = collection.find({'phoneName': username})
            cursor = collection.find()

            # 遍历 Cursor 对象
            for document in cursor:
                print(document)




            # print(result)

            user = User_Info(userName=result['userName'], userId=result['userId'])
            user_id = user.userId
            print(user_id)

            rClient = redis.Redis(
                host='192.168.3.171',  # Redis 服务器的主机名或 IP 地址
                port=16378,  # Redis 服务器的端口，默认是 6379
                password='ohqnrRxS1FPvVXkI',
                db=0,  # 默认数据库选择，通常是 0
                decode_responses=True  # 使得操作返回字符串（而不是字节）
            )

            getToken = rClient.get("userInfo:pclodelSingleToken:" + user_id)

            getUserInfo = rClient.get("userInfo:appUserSession:" + getToken)
            print(getUserInfo)
        except Exception as e:
            print(e)

class User_Info:
    def __init__(self, userName, userId):
        self.userName = userName
        self.userId = userId

if __name__ == '__main__':
    connection = DatabaseConnection()
    connection.connect_mongodb("15727576786")





