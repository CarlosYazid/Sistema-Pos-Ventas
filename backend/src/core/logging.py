import asyncio
from functools import wraps
from time import perf_counter
from typing import Any, Callable

import logfire
from pydantic import BaseModel
from sqlmodel import SQLModel

PRIMITIVES = (str, int, float, bool, type(None))


def sanitize_value(value: Any):
    if isinstance(value, PRIMITIVES):
        return value

    if isinstance(value, (list, tuple)):
        return [sanitize_value(v) for v in value]

    if isinstance(value, dict):
        return {k: sanitize_value(v) for k, v in value.items()}

    if isinstance(value, BaseModel):
        return value.model_dump(exclude_none=True)

    if isinstance(value, SQLModel):
        return value.model_dump(exclude_none=True)

    return f"<{value.__class__.__name__}>"


def log_operation(log_args: bool = False):
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = perf_counter()

            with logfire.span(func.__doc__ or func.__name__) as span:
                try:
                    if log_args:
                        span.set_attribute("args", sanitize_value(args))

                        if kwargs:
                            span.set_attribute("kwargs", sanitize_value(kwargs))

                    result = await func(*args, **kwargs)
                    span.set_attribute("success", True)

                    return result

                except Exception as e:
                    span.set_attribute("success", False)
                    span.set_attribute("error", str(e))

                    raise

                finally:
                    span.set_attribute("duration_ms", (perf_counter() - start_time) * 1000)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = perf_counter()

            with logfire.span(func.__doc__ or func.__name__) as span:
                try:
                    if log_args:
                        span.set_attribute("args", sanitize_value(args))

                        if kwargs:
                            span.set_attribute("kwargs", sanitize_value(kwargs))

                    result = func(*args, **kwargs)
                    span.set_attribute("success", True)

                    return result

                except Exception as e:
                    span.set_attribute("success", False)
                    span.set_attribute("error", str(e))

                    raise

                finally:
                    span.set_attribute("duration_ms", (perf_counter() - start_time) * 1000)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator
