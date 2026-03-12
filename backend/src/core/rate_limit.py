from slowapi import Limiter
from slowapi.util import get_remote_address

LIMITER = Limiter(
    key_func=get_remote_address,
    headers_enabled=True,
    default_limits=[
        "120/minute",  # limite sostenido
        "30/second",  # controla picos/bursts
    ],
)
