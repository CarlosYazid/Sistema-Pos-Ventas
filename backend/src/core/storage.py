import aioboto3
from botocore.client import Config

from .settings import SETTINGS

SESSION = aioboto3.Session()


async def get_e2_client():
    async with SESSION.client(
        "s3",
        endpoint_url=SETTINGS.storage_endpoint_url,
        aws_access_key_id=SETTINGS.storage_access_key.get_secret_value(),
        aws_secret_access_key=SETTINGS.storage_secret_key.get_secret_value(),
        region_name=SETTINGS.storage_region,
        config=Config(signature_version="s3v4"),
    ) as e2:
        yield e2
