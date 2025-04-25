import logging
import functools

def log_call(func):
    """
    Decorator to log function entry, exit, arguments, and exceptions.
    Handles both sync and async functions.
    """
    if hasattr(func, "__code__") and func.__code__.co_flags & 0x80:
        # Async function
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            logging.debug(f"[async] Entering {func.__qualname__} args={args} kwargs={kwargs}")
            try:
                result = await func(*args, **kwargs)
                logging.debug(f"[async] Exiting {func.__qualname__} result={result}")
                return result
            except Exception as e:
                logging.error(f"[async] Exception in {func.__qualname__}: {e}", exc_info=True)
                raise
        return async_wrapper
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            logging.debug(f"Entering {func.__qualname__} args={args} kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logging.debug(f"Exiting {func.__qualname__} result={result}")
                return result
            except Exception as e:
                logging.error(f"Exception in {func.__qualname__}: {e}", exc_info=True)
                raise
        return sync_wrapper
