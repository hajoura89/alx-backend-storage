import requests
import redis
from functools import wraps
from time import time

""" Connect to Redis server"""
redis_client = redis.Redis()


def cache_with_expiry(expiration_time):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            url = args[0]
            cache_key = f"cache:{url}"
            count_key = f"count:{url}"

            """Check if the result is in the cache"""
            cached_result = redis_client.get(cache_key)
            if cached_result:
                """If cached, increment the access count"""
                redis_client.incr(count_key)
                return cached_result.decode('utf-8')

            """If not in cache, fetch from the web"""
            result = func(*args, **kwargs)

            """Cache the result with an expiration time"""
            redis_client.setex(cache_key, expiration_time, result)

            """Increment the access count"""
            redis_client.incr(count_key)

            return result

        return wrapper
    return decorator


@cache_with_expiry(10)
def get_page(url):
    """Simulate a slow response using
    slowwly.robertomurray.co.uk"""
    response = requests.get(url)
    return response.text


"""Example usage"""
if __name__ == "__main__":
    url = (
        "http://slowwly.robertomurray.co.uk/delay/10000/"
        "url/http://www.google.com"
    )

    """Access the page multiple times"""
    for _ in range(5):
        print(get_page(url))

    """Print access count"""
    count_key = f"count:{url}"
    access_count = redis_client.get(count_key)
    print(f"Access count for {url}: {int(access_count)}")
