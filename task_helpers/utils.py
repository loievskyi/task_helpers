import redis


def get_aioredis_connection(redis_connection):
    connection_kwargs = redis_connection.connection_pool.connection_kwargs
    connection_kwargs = {
        "username": connection_kwargs["username"],
        "password": connection_kwargs["password"],
        "host": connection_kwargs["host"],
        "port": connection_kwargs["port"],
        "db": connection_kwargs["db"],
    }
    return redis.asyncio.Redis(**connection_kwargs)
