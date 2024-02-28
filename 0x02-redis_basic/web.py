#!/usr/bin/env python3
"""Implementing an expiring web cache and tracker"""
import redis
import requests
from functools import wraps

redis_store = redis.Redis()


def data_cacher(method: Callable) -> Callable:
    """Caches the output of fetched data"""
    @wraps(method)
    def wrapper(url):
        """wrapper function"""
        key = "cached:" + url
        cached_value = redis_store.get(key)
        if cached_value:
            return cached_value.decode("utf-8")

            # Get new content and update cache
        key_count = "count:" + url
        html_content = method(url)

        redis_store.incr(key_count)
        redis_store.set(key, html_content, ex=10)
        redis_store.expire(key, 10)
        return html_content
    return wrapper


@data_cacher
def get_page(url: str) -> str:
    """Returns the HTML content of a URL"""
    return requests.get(url).text
 

if __name__ == "__main__":
    get_page('http://slowwly.robertomurray.co.uk')
