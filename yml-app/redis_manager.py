import redis


class RedisException(Exception):
    """ Exception caused in redis """
    pass


class RedisManager:

    default_host = "localhost"
    defaut_port = 6379
    default_pwd = ""

    def __init__(self, host=default_host, port=defaut_port, pwd=default_pwd):
        self.host = host
        self.port = port
        self.pwd = pwd

        self.server_connect()

    def server_connect(self):
        try:
            self.redis = redis.StrictRedis(
                host=self.host,
                port=self.port,
                password=self.pwd,
                decode_responses=True
            )

        except Exception as err:
            raise RedisException(err)

    def set(self, key, value):
        self.redis.set(key, value)

    def get(self, key):
        return self.redis.get(key)

    def scan_iter(self, match=None, count=None):
        return self.redis.scan_iter(match, count)

    # TODO: disconnect server
