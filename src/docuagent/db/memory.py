from langgraph.checkpoint.redis import RedisSaver
from langgraph.checkpoint.redis.shallow import ShallowRedisSaver 
from docuagent.config.settings import settings

def get_redis_checkpoint() -> RedisSaver:
    """Get Redis checkpoint."""
    checkpointer = ShallowRedisSaver(redis_url = settings.redis_url, ttl = settings.ttl_config)
    checkpointer.setup()

    return checkpointer 



    