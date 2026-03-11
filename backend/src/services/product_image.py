from botocore.client import BaseClient
from fastapi import UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession

from core import NotFoundError, UpdateError
from models import Product
from services.abc import AbstractService


class ProductImageService:
    def __init__(self, product_service: AbstractService | None = None, utils: object | None = None):
        self.product_service = product_service
        self.utils = utils

    async def update_image(
        self, product_id: int, image: UploadFile, session: AsyncSession, storage_client: BaseClient
    ) -> Product:
        if not await self.product_service.exists(product_id, session):
            raise NotFoundError("Product")

        try:
            product = await self.product_service.read(product_id, session)

            old_key = product.image_key

            new_key = await self.utils.upload_image(image, storage_client)

            product.image_key = new_key

            if old_key:
                await self.utils.delete_image(old_key, storage_client)

            session.add(product)

            await session.commit()
            await session.refresh(product)

            return product

        except SQLAlchemyError as e:
            await session.rollback()

            raise UpdateError("Image") from e
