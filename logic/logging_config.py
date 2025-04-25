import logging
import functools
import inspect
import threading
import os

def log_call(func):
    """
    Enhanced decorator to log function entry, exit, arguments, class, caller, thread, and process info.
    Handles both sync and async functions.
    """
    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            cls = args[0].__class__.__name__ if args and hasattr(args[0], '__class__') else None
            caller = inspect.stack()[1]
            logging.debug(
                f"[async] Entering {func.__qualname__} (class={cls}) "
                f"args={args} kwargs={kwargs} "
                f"called_from={caller.function}:{caller.lineno} "
                f"thread={threading.current_thread().name} pid={os.getpid()}"
            )
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
            cls = args[0].__class__.__name__ if args and hasattr(args[0], '__class__') else None
            caller = inspect.stack()[1]
            logging.debug(
                f"Entering {func.__qualname__} (class={cls}) "
                f"args={args} kwargs={kwargs} "
                f"called_from={caller.function}:{caller.lineno} "
                f"thread={threading.current_thread().name} pid={os.getpid()}"
            )
            try:
                result = func(*args, **kwargs)
                logging.debug(f"Exiting {func.__qualname__} result={result}")
                return result
            except Exception as e:
                logging.error(f"Exception in {func.__qualname__}: {e}", exc_info=True)
                raise
        return sync_wrapper
