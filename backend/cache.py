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
    brand_description: str,
    tone: str,
    target_audience: str,
    goal: str,
    num_variants: int,
) -> str:
    product = " ".join(product_name.lower().split())
    description = " ".join(brand_description.lower().split())
    tone_norm = " ".join(tone.lower().split())
    audience = " ".join(target_audience.lower().split())
    goal_norm = " ".join(goal.lower().split())
    combined = f"v2:{product}:{description}:{tone_norm}:{audience}:{goal_norm}:{num_variants}"
    return hashlib.md5(combined.encode()).hexdigest()


def check_rate_limit(identifier: str, limit: int = 5, window: int = 60) -> bool:
    try:
        key = f"ratelimit:{identifier}"
        count = redis_client.incr(key)
        if count == 1 or redis_client.ttl(key) == -1:
            redis_client.expire(key, window)
        return count <= limit
    except Exception:
        return True
