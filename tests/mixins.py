import os

import redis


class RedisSetupMixin:
    """
    mixin for redis connection initializing.
    """

    def setUp(self):
        redis_host = os.environ.get("REDIS_HOST")
        redis_port = os.environ.get("REDIS_PORT")
        redis_db = os.environ.get("REDIS_DB")
        redis_password = os.environ.get("REDIS_PASSWORD", None)

        assert redis_host is not None, "redis_host is None"
        assert redis_port is not None, "redis_port is None"
        assert redis_db is not None, "redis_db is None"

        self.redis_connection = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password)
        self.redis_connection.flushdb()
