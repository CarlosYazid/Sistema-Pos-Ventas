from fastapi import status

# ------- BASE ---------


class ApplicationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


# ------- DB ---------


class DBError(ApplicationError):
    def __init__(self, message: str):
        super().__init__(message)


# 404
class NotFoundError(DBError):
    def __init__(self, entity: str):
        super().__init__(f"{entity} not found")


# 409
class EntityAlreadyExistsError(DBError):
    def __init__(self, entity: str):
        super().__init__(f"You are trying to add the entity {entity} more than twice.")


class EmployeeAlreadyExistsError(EntityAlreadyExistsError):
    def __init__(self, email: str):
        super().__init__(f"employee with email {email}")


class EmployeeProfileAlreadyCompletedError(DBError):
    def __init__(self, email: str):
        super().__init__(f"employee profile is already completed for {email}")


# 500
class CreationError(DBError):
    def __init__(self, entity: str):
        super().__init__(f"{entity} creation failed")


# 500
class ReadingError(DBError):
    def __init__(self, entity: str):
        super().__init__(f"{entity} read failed")


# 500
class UpdateError(DBError):
    def __init__(self, entity: str):
        super().__init__(f"{entity} update failed")


# 500
class DeletionError(DBError):
    def __init__(self, entity: str):
        super().__init__(f"{entity} delete failed")


# ------- Service ---------


class ServiceError(ApplicationError):
    def __init__(self, message: str):
        super().__init__(message)


class ServiceAlreadyAddedToOrderError(ServiceError):
    def __init__(self, service_name: str):
        super().__init__(f"Service {service_name} is already associated to this order")


# ------- Product ---------


class ProductError(ApplicationError):
    def __init__(self, message: str):
        super().__init__(message)


class ProductAlreadyAddedToOrderError(ProductError):
    def __init__(self, product_name: str):
        super().__init__(f"Product {product_name} is already associated to this order")


class ProductAlreadyAddedToCategoryError(ProductError):
    def __init__(self, product_name: str, category_name: str):
        super().__init__(f"Product {product_name} is already in category {category_name}")


# 406
class InsufficientStockError(ProductError):
    def __init__(self, product_name: str):
        super().__init__(f"Insufficient stock for {product_name}")


# 406
class ExpiredProductError(ProductError):
    def __init__(self, product_name: str):
        super().__init__(f"Product {product_name} has expired.")


# ------- Storage ---------


class StorageError(ApplicationError):
    def __init__(self, message: str):
        super().__init__(message)


# 500
class RetrievingFileError(StorageError):
    def __init__(self):
        super().__init__("There was an error retrieving the file.")


# 404
class FileNotFoundError(StorageError):
    def __init__(self, key: str):
        super().__init__(f"file not found in the key {key}")


# ------- Infrastructure ---------


# 415
class InvalidImageTypeError(ApplicationError):
    def __init__(self, content_type: str, allowed_types: str):
        super().__init__(f"Invalid image type: {content_type}. Allowed types are: {allowed_types}")


# 400
class MissingFieldError(ApplicationError):
    def __init__(self, field: str):
        super().__init__(f"The field {field} is required")


ERROR_STATUS_CODE = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    EntityAlreadyExistsError: status.HTTP_409_CONFLICT,
    EmployeeProfileAlreadyCompletedError: status.HTTP_409_CONFLICT,
    CreationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ReadingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    UpdateError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    DeletionError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    InsufficientStockError: status.HTTP_406_NOT_ACCEPTABLE,
    ExpiredProductError: status.HTTP_406_NOT_ACCEPTABLE,
    ProductAlreadyAddedToOrderError: status.HTTP_409_CONFLICT,
    ProductAlreadyAddedToCategoryError: status.HTTP_409_CONFLICT,
    ServiceAlreadyAddedToOrderError: status.HTTP_409_CONFLICT,
    EmployeeAlreadyExistsError: status.HTTP_409_CONFLICT,
    RetrievingFileError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    FileNotFoundError: status.HTTP_404_NOT_FOUND,
    InvalidImageTypeError: status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
}

ERROR_HTTP_MAPPING = ERROR_STATUS_CODE
