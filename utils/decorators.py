# utils/decorators.py

import time
import logging
import functools

def log_block(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"[START] {func.__name__} {args[0].__class__}")
        s_time = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            duration = time.time() - s_time
            logging.info(f"[END] {func.__name__} {args[0].__class__} {duration:.2f} seconds")
    return wrapper



def log_block_async(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logging.info(f"[START] {func.__name__} {args[0].__class__}")
        start = time.time()
        try:
            return await func(*args, **kwargs)
        finally:
            duration = time.time() - start
            logging.info(f"[END] {func.__name__} {args[0].__class__} ({duration:.2f}s)")
    return wrapper