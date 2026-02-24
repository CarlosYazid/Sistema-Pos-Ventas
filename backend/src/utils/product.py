from uuid import uuid4

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi import HTTPException, UploadFile
from botocore.client import BaseClient

from models import Product, Category, ProductCategory
from core import SETTINGS, log_operation

class ProductUtils:
    
    ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp"}
    
    @staticmethod
    @log_operation(True)
    async def exist_product(db_session: AsyncSession, product_id: int) -> bool:
        """Check if a product exists by ID."""
        
        try:
            
            response = await db_session.exec(select(Product).where(Product.id == product_id))
            
            return bool(response.first())
        
        except Exception as e:
            raise HTTPException(detail="Product existence check failed", status_code=500) from e
        
    @staticmethod
    @log_operation(False)
    async def upload_image(storage_client : BaseClient, image: UploadFile) -> str:
        """Upload an image to the storage."""

        if image.content_type not in ProductUtils.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid image type: {image.content_type}. "
                    f"Allowed types are: {', '.join(ProductUtils.ALLOWED_IMAGE_TYPES)}"
                ),
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

    @staticmethod
    @log_operation(True)
    async def delete_image(cls, storage_client: BaseClient, image_key: str) -> None:
        """Delete an image from the storage."""

        await storage_client.delete_object(Bucket=SETTINGS.bucket_name, Key=image_key)
    
    @staticmethod
    @log_operation(True)
    async def exist_category(cls, db_session: AsyncSession, category_id: int) -> bool:
        """Check if a category exists by ID."""
        
        try:
            
            response = await db_session.exec(select(Category).where(Category.id == category_id))

            return bool(response.first())
        
        except Exception as e:
            raise HTTPException(detail="Category existence check failed", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def exist_product_category(cls, db_session: AsyncSession, product_category: ProductCategory) -> bool:
        """Check if a product category exists by ID."""

        try:
            
            response = await db_session.exec(select(ProductCategory).where(ProductCategory.product_id == product_category.product_id, ProductCategory.category_id == product_category.category_id))
            
            return bool(response.first())
        
        except Exception as e:
            raise HTTPException(detail="Product category existence check failed", status_code=500) from e
