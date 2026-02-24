from fastapi import HTTPException, UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from botocore.client import BaseClient

from models import Product, ProductCategory, Category
from utils import ProductUtils
from dtos import ProductCreate, ProductUpdate, CategoryCreate, CategoryUpdate
from core import log_operation

class ProductCrud:
    
    EXCLUDED_FIELDS_FOR_UPDATE = {"id"}

    @staticmethod
    @log_operation(True)
    async def create_product(db_session: AsyncSession, product: ProductCreate) -> Product:
        """Create a new product."""
                    
        try:
            
            new_product = Product(**product.model_dump(exclude_unset=True))
            db_session.add(new_product)

            await db_session.commit()
            await db_session.refresh(new_product)
            
            return new_product
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(status_code=500, detail="Service creation failed") from e
    
    @staticmethod
    @log_operation(True)
    async def read_product(db_session: AsyncSession, product_id: int) -> Product:
        """Retrieve a product by ID."""
        
        try:
            
            response = await db_session.exec(select(Product).where(Product.id == product_id))
            product = response.first()
            
            if product is None:
                raise HTTPException(detail="Product not found", status_code=404)
            
            return product
        
        except Exception as e:
            raise HTTPException(detail="Product search failed", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def update_product(db_session: AsyncSession, fields: ProductUpdate) -> Product:
        """Update an existing product."""
        
        # Check if the product exists before attempting to update
        if not await ProductUtils.exist_product(db_session, fields.id):
            raise HTTPException(detail="Product not found", status_code=404)
        
        try:
            
            response = await db_session.exec(select(Product).where(Product.id == fields.id))
            product = response.one()
            
            for key, value in fields.model_dump(exclude_unset=True).items():
                    
                if key in ProductCrud.EXCLUDED_FIELDS_FOR_UPDATE:
                    continue
                    
                setattr(product, key, value)

            db_session.add(product)
            await db_session.commit()
                
            await db_session.refresh(product)
            return product
            
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Product update failed", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def update_stock(db_session: AsyncSession, product_id: int, new_stock: int, replace: bool = True) -> Product:
        """Update the stock of a product by ID."""

        # Check if the product exists before attempting to update stock
        if not await ProductUtils.exist_product(db_session, product_id):
            raise HTTPException(detail="Product not found", status_code=404)
        try:
            
            response = await db_session.exec(select(Product).where(Product.id == product_id))
            product = response.one()

            if replace:
                product.stock = new_stock
            else:
                product.stock += new_stock

            if product.stock < 0:
                product.stock = 0

            db_session.add(product)
            
            await db_session.commit()
            await db_session.refresh(product)
            
            return product
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Stock update failed", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def update_image(db_session: AsyncSession, storage_client: BaseClient, product_id: int, image: UploadFile) -> Product:
        """Update the image of a product by ID."""

        # Check if the product exists before attempting to update the image
        if not await ProductUtils.exist_product(db_session, product_id):
            raise HTTPException(detail="Product not found", status_code=404)
        
        try:
            
            response = await db_session.exec(select(Product).where(Product.id == product_id))
            product = response.one()

            old_image_key = product.image_key 

            image_key = await ProductUtils.upload_image(storage_client, image)

            product.image_key = image_key

            db_session.add(product)

            await db_session.commit()
            await db_session.refresh(product)
            
            if not old_image_key is None:
                await ProductUtils.delete_image(storage_client, old_image_key)
            
            return product
    
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Image update failed", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def delete_product(db_session: AsyncSession, storage_client: BaseClient, product_id: int) -> bool:
        """Delete a product by ID."""

        # Check if the product exists before attempting to delete
        if not await ProductUtils.exist_product(db_session, product_id):
            raise HTTPException(detail="Product not found", status_code=404)
        
        from utils import OrderUtils
        
        # Check if the product is associated with any orders
        if await OrderUtils.exist_product_in_orders(db_session, product_id):
            raise HTTPException(detail="Cannot delete product associated with orders", status_code=400)
        
        try:

            image_key = None

            response = await db_session.exec(select(Product).where(Product.id == product_id))
            product = response.one()

            if not product.image_key is None:
                image_key = product.image_key

            await db_session.delete(response.one())
            await db_session.commit()
            
            if not image_key is None:
                await ProductUtils.delete_image(storage_client, image_key)

            return True
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Product deletion failed", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def create_product_category(db_session: AsyncSession, product_category: ProductCategory) -> ProductCategory:
        """Create a new product category."""
        
        if not await ProductUtils.exist_product(db_session, product_category.product_id):
            raise HTTPException(detail="Product not found", status_code=404)
        
        if not await ProductUtils.exist_category(db_session, product_category.category_id):
            raise HTTPException(detail="Category not found", status_code=404)

        try:

            db_session.add(product_category)
            
            await db_session.commit()
            await db_session.refresh(product_category)
            
            return product_category
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Failed to create product category", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def delete_product_category(db_session: AsyncSession, product_category: ProductCategory) -> bool:
        """Delete a product category by ID."""

        # Check if the category exists before attempting to delete
        if not await ProductUtils.exist_product_category(db_session, product_category):
            raise HTTPException(detail="Product Category not found", status_code=404)
        
        try:
            
            response = await db_session.exec(select(ProductCategory).where(ProductCategory.product_id == product_category.product_id, ProductCategory.category_id == product_category.category_id))

            await db_session.delete(response.one())
            await db_session.commit()
            
            return True

        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Product category deletion failed", status_code=500) from e

    @staticmethod
    @log_operation(True)
    async def create_category(db_session: AsyncSession, category: CategoryCreate) -> Category:
        """Create a new product category."""
        
        try:
            
            new_category = Category(**category.model_dump(exclude_unset=True))
            db_session.add(new_category)
            
            await db_session.commit()
            await db_session.refresh(new_category)
            
            return new_category
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Failed to create category", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def read_category(db_session: AsyncSession, category_id: int) -> Category:
        """Retrieve a product category by ID."""
        
        try:
            
            response = await db_session.exec(select(Category).where(Category.id == category_id))
            category = response.first()

            if category is None:
                raise HTTPException(detail="Category not found", status_code=404)

            return category
        
        except Exception as e:
            raise HTTPException(detail="Failed to retrieve category", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def update_category(db_session: AsyncSession, fields: CategoryUpdate) -> Category:
        """Update an existing product category."""
        
        # Check if the category exists before attempting to update
        if not await ProductUtils.exist_category(db_session, fields.id):
            raise HTTPException(detail="Category not found", status_code=404)
        
        try:
            
            response = await db_session.exec(select(Category).where(Category.id ==fields.id))
            category = response.one()

            for key, value in fields.model_dump(exclude_unset=True).items():
                    
                if key in cls.EXCLUDED_FIELDS_FOR_UPDATE:
                    continue

                setattr(category, key, value)

            db_session.add(category)
            await db_session.commit()
                
            await db_session.refresh(category)
            return category
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Failed to update category", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def delete_category(db_session: AsyncSession, category_id: int) -> bool:
        """Delete a product category by ID."""

        # Check if the category exists before attempting to delete
        if not await ProductUtils.exist_category(db_session, category_id):
            raise HTTPException(detail="Category not found", status_code=404)
        
        try:
            
            response = await db_session.exec(select(Category).where(Category.id == category_id))
            
            await db_session.delete(response.one())
            await db_session.commit()
            
            return True
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Failed to delete category", status_code=500) from e
