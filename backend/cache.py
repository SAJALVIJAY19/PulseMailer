from upstash_redis import Redis
import json
import hashlib
from dotenv import load_dotenv

load_dotenv()

redis_client = Redis.from_env()


def get_cached_response(key: str) -> dict:
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception:
        return None


def set_cached_response(key: str, value: dict, ttl: int = 86400):
    try:
        redis_client.setex(key, ttl, json.dumps(value))
    except Exception:
        pass


def generate_cache_key(
    product_name: str,
    tone: str,
    target_audience: str,
    goal: str,
    num_variants: int,
) -> str:
    combined = f"{product_name}:{tone}:{target_audience}:{goal}:{num_variants}"
    return hashlib.md5(combined.encode()).hexdigest()
