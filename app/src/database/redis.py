import json
import os

import redis.asyncio as redis

# Environment variable/s
REDIS_HOST = os.getenv("REDIS_HOST", None)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_LIST_LIMIT = int(os.getenv("REDIS_LIST_LIMIT", 30))

if REDIS_HOST is None or REDIS_PASSWORD is None:
    raise ValueError("Redis environment variables are not set.")


class RedisClient:
    """
    Client for Redis database.
    """

    def __init__(self) -> None:
        """
        Constructor method for `RedisClient`.
        """
        self.client = redis.Redis(host=REDIS_HOST, password=REDIS_PASSWORD)

    async def close(self) -> None:
        """
        Close the Redis client.
        """
        await self.client.aclose()

    async def ping(self) -> None:
        """
        Ping the Redis client.
        """
        await self.client.ping()

    async def push(self, key: str, content: list[dict]) -> None:
        """
        Push content to a list in Redis with the given key.

        Parameters
        ----------
        key : str
            The key of the list.

        content : list[dict]
            The content to push to the list.
        """
        for item in content:
            item = json.dumps(item)
            await self.client.rpush(key, item)

            # Check if the list is too long
            if await self.length(key) > REDIS_LIST_LIMIT:
                await self.pop(key)

    async def pop(self, key: str) -> None:
        """
        Pop the first item from a list in Redis with the given key.

        Parameters
        ----------
        key : str
            The key of the list.
        """
        await self.client.lpop(key)

    async def get(self, key: str) -> list[dict] | None:
        """
        Get all items from a list in Redis with the given key.

        Parameters
        ----------
        key : str
            The key of the list.

        Returns
        -------
        items : list[dict] | None
            The items in the list.
            If the list is empty, return None.
        """
        items = await self.client.lrange(key, 0, -1)
        items = [json.loads(item) for item in items]
        if len(items) == 0:
            return None
        return items

    async def length(self, key: str) -> int:
        """
        Get the length of a list in Redis with the given key.

        Parameters
        ----------
        key : str
            The key of the list.

        Returns
        -------
        length : int
            The length of the list.
        """
        return await self.client.llen(key)
