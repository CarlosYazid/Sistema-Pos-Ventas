from repositories import ProductCategoryRepository

from .abc import BaseAssociationService


class ProductCategoryService(BaseAssociationService[ProductCategoryRepository]):
    def __init__(self, fields_exclude: set[str] | None = None):
        super().__init__(ProductCategoryRepository(fields_exclude))
