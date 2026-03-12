from models import ProductCategory
from repositories.abc import BaseAssociationRepository


class ProductCategoryRepository(BaseAssociationRepository[ProductCategory]):
    def __init__(self, fields_exclude: set[str] | None = None):
        super().__init__(ProductCategory, fields_exclude)
