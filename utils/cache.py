#utils/cache.py
import redis
from dotenv import load_dotenv

# Specify the path to the .env file
dotenv_path = "myenv/.env"

# Load environment variables from the specified .env file
load_dotenv(dotenv_path)

#This utitly caches data like tokens e.t.c
redis_cache = redis.StrictRedis(host='localhost', port=6379, db=0)

def cache_data(key, data):
    redis_cache.set(key, data)

def get_cached_data(key):
    return redis_cache.get(key)
