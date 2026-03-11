from uuid import uuid4

from botocore.client import BaseClient
from fastapi import UploadFile

from core import SETTINGS, InvalidImageTypeError, log_operation


class ProductUtils:
    ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp"}

    @log_operation(False)
    async def upload_image(self, image: UploadFile, storage_client: BaseClient) -> str:
        """Upload an image to the storage."""

        if image.content_type not in ProductUtils.ALLOWED_IMAGE_TYPES:
            raise InvalidImageTypeError(
                image.content_type, ", ".join(ProductUtils.ALLOWED_IMAGE_TYPES)
            )

        await image.seek(0)

        safe_name = f"{uuid4()}-{image.filename}"
        image_key = f"{SETTINGS.image_folder}/{safe_name}"

        await storage_client.upload_fileobj(
            image.file,
            SETTINGS.bucket_name,
            image_key,
            ExtraArgs={"ContentType": image.content_type},
        )

        return image_key

    @log_operation(True)
    async def delete_image(self, image_key: str, storage_client: BaseClient) -> None:
        """Delete an image from the storage."""

        await storage_client.delete_object(Bucket=SETTINGS.bucket_name, Key=image_key)
