import pytest
from pymongo import MongoClient

#mongodb连接配置(ssh)
MONGODB_HOST  = "127.0.0.1"
MONGODB_PORT = 27019 #本地侦听端口
DB_NAME = "k8sMongodb"  # Navicat中配置的数据库名
COLLECTTION_NAME = "im" # 替换为实际集合名

#封装mongodb工具类
class MongoDBHelper:
    def __init__(self):
        self.client = MongoClient(f"mongodb://{MONGODB_HOST}:{MONGODB_PORT}/")
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTTION_NAME]
    def query_data(self,filter_query=None): #查询数据
        if filter_query is None:
            filter_query = {}
        return list(self.collection.find(filter_query))
    def close_connection(self): #关闭连接
        self.client.close()


@pytest.fixture(scope="module")
def mongodb():
    db = MongoDBHelper()
    yield db
    db.close_connection()

