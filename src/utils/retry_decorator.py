"""
API调用重试装饰器 - 自动重试网络和API错误
"""
import time
from functools import wraps
import ccxt
from requests.exceptions import RequestException, ConnectionError, Timeout


def retry_on_api_error(max_retries=3, delay=2, backoff=2):
    """
    API调用重试装饰器

    自动重试网络错误和API错误，使用指数退避策略

    Args:
        max_retries: 最大重试次数（默认3次）
        delay: 初始延迟秒数（默认2秒）
        backoff: 延迟倍数，用于指数退避（默认2倍）

    Example:
        @retry_on_api_error(max_retries=3, delay=2)
        def get_market_data():
            return client.futures_klines(...)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except (ccxt.NetworkError, ccxt.ExchangeError, RequestException, ConnectionError, Timeout) as e:
                    retries += 1
                    if retries >= max_retries:
                        print(f"❌ {func.__name__} 重试{max_retries}次后仍失败: {e}")
                        raise

                    print(f"⚠️ {func.__name__} 失败，{current_delay}秒后重试 ({retries}/{max_retries}): {e}")
                    time.sleep(current_delay)
                    current_delay *= backoff  # 指数退避：2s -> 4s -> 8s

        return wrapper
    return decorator


def retry_on_network_error(max_retries=5, delay=1, backoff=1.5):
    """
    网络错误重试装饰器（更激进的重试策略）

    用于关键的网络操作，重试次数更多，延迟更短

    Args:
        max_retries: 最大重试次数（默认5次）
        delay: 初始延迟秒数（默认1秒）
        backoff: 延迟倍数（默认1.5倍）

    Example:
        @retry_on_network_error(max_retries=5)
        def connect_to_exchange():
            return Client(api_key, api_secret)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except (ConnectionError, Timeout, RequestException) as e:
                    retries += 1
                    if retries >= max_retries:
                        print(f"❌ {func.__name__} 网络连接重试{max_retries}次后仍失败: {e}")
                        raise

                    print(f"⚠️ {func.__name__} 网络错误，{current_delay:.1f}秒后重试 ({retries}/{max_retries})")
                    time.sleep(current_delay)
                    current_delay *= backoff  # 指数退避：1s -> 1.5s -> 2.25s -> 3.4s -> 5.1s

        return wrapper
    return decorator
