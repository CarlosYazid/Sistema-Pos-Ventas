from urllib.parse import quote

from botocore.client import BaseClient
from botocore.exceptions import ClientError
from fastapi.responses import StreamingResponse

from core.errors import FileNotFoundError, RetrievingFileError
from core.settings import SETTINGS


class FileService:
    async def get_file(self, key: str, storage_client: BaseClient) -> StreamingResponse:
        """Retrieve a file by name."""

        obj = {}

        try:
            obj = await storage_client.get_object(Bucket=SETTINGS.bucket_name, Key=key)

        except ClientError as e:
            if e.response["Error"]["Code"] in ("404", "NoSuchKey"):
                raise FileNotFoundError(key) from e

            raise RetrievingFileError() from e

        content_type = obj.get("ContentType", "application/octet-stream")

        return StreamingResponse(
            obj.get("Body", None),
            media_type=content_type,
            headers={"Content-Disposition": f'inline; filename="{quote(key.split("/")[-1])}"'},
        )
