import logging
import functools
import inspect
import threading
import os

ASYNC_LOG_PREFIX = '[async] '

def _log_entry(func, cls, args, kwargs, caller, is_async=False):
    """
    Log the entry of a function, including arguments, caller, thread, and process info.
    """
    prefix = ASYNC_LOG_PREFIX if is_async else ''
    logging.debug(
        f"{prefix}Entering {func.__qualname__} (class={cls}) "
        f"args={args} kwargs={kwargs} "
        f"called_from={caller.function}:{caller.lineno} "
        f"thread={threading.current_thread().name} pid={os.getpid()}"
    )

def _log_exit(func, result, is_async=False):
    """
    Log the exit of a function, including its result.
    """
    prefix = ASYNC_LOG_PREFIX if is_async else ''
    logging.debug(f"{prefix}Exiting {func.__qualname__} result={result}")

def _log_exception(func, e, is_async=False):
    """
    Log an exception raised in a function.
    """
    prefix = ASYNC_LOG_PREFIX if is_async else ''
    logging.error(f"{prefix}Exception in {func.__qualname__}: {e}", exc_info=True)


def log_call(func):
    """
    Decorator to log function entry, exit, arguments, class, caller, thread, and process info.
    Handles both sync and async functions.
    """
    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            """
            Asynchronous wrapper for logging function calls.
            """
            cls = args[0].__class__.__name__ if args and hasattr(args[0], '__class__') else None
            caller = inspect.stack()[1]
            _log_entry(func, cls, args, kwargs, caller, is_async=True)
            try:
                result = await func(*args, **kwargs)
                _log_exit(func, result, is_async=True)
                return result
            except Exception as e:
                _log_exception(func, e, is_async=True)
                raise
        return async_wrapper
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            """
            Synchronous wrapper for logging function calls.
            """
            cls = args[0].__class__.__name__ if args and hasattr(args[0], '__class__') else None
            caller = inspect.stack()[1]
            _log_entry(func, cls, args, kwargs, caller)
            try:
                result = func(*args, **kwargs)
                _log_exit(func, result)
                return result
            except Exception as e:
                _log_exception(func, e)
                raise
        return sync_wrapper
