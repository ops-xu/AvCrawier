import redis
import configparser
from pathlib import Path


class RedisPool:
    instance = None

    def __init__(self):
        config = configparser.ConfigParser()
        config.read(Path(__file__).resolve().parent.parent / 'config/config.ini')
        host = config.read('redis', 'host')
        port = config.read('redis', 'port')
        db = config.read('redis', 'db')
        password = config.read('redis', 'password')
        self.pool = redis.ConnectionPool(host=host, port=port, decode_responses=True, db=db,
                                         password=password)

    def __getConnection(self):
        conn = redis.Redis(connection_pool=self.pool)
        return conn

    @classmethod
    def getConn(cls):
        if RedisPool.instance is None:
            RedisPool.instance = RedisPool()
        return RedisPool.instance.__getConnection()


redisPool = RedisPool()
