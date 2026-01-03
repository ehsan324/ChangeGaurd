from app.core.redis_client import redis_client

class DistributedLock:
    def __init__(self, key: str, ttl_seconds: int = 30):
        self.key = key
        self.ttl_seconds = ttl_seconds
        self.acquired = False

    def acquire(self) -> bool:
        self.acquired = redis_client.set(
            self.key,
            "1",
            nx=True,
            ex=self.ttl_seconds,
        )
        return bool(self.acquired)

    def release(self) -> None:
        if self.acquired:
            redis_client.delete(self.key)
            self.acquired = False
