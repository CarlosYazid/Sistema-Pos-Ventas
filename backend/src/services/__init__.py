from importlib import import_module

_EXPORT_MAP = {
    "AbstractService": ("services.abc", "AbstractService"),
    "AbstractAssociationService": ("services.abc", "AbstractAssociationService"),
    "BaseService": ("services.abc", "BaseService"),
    "BaseAssociationService": ("services.abc", "BaseAssociationService"),
    "UserService": ("services.abc", "UserService"),
    "ClientService": ("services.client", "ClientService"),
    "EmployeeService": ("services.employee", "EmployeeService"),
    "ProductService": ("services.product", "ProductService"),
    "CategoryService": ("services.category", "CategoryService"),
    "ProductCategoryService": ("services.product_category", "ProductCategoryService"),
    "ProductImageService": ("services.product_image", "ProductImageService"),
    "ServiceService": ("services.service", "ServiceService"),
    "ServiceInputService": ("services.service_input", "ServiceInputService"),
    "OrderService": ("services.order", "OrderService"),
    "OrderProductService": ("services.order_product", "OrderProductService"),
    "OrderServiceService": ("services.order_service", "OrderServiceService"),
    "InventoryService": ("services.inventory", "InventoryService"),
    "PaymentService": ("services.payment", "PaymentService"),
    "FileService": ("services.file", "FileService"),
    "InvoiceService": ("services.invoice", "InvoiceService"),
    "EmailService": ("services.email", "EmailService"),
    "SuperTokensEmailVerificationService": (
        "services.email",
        "SuperTokensEmailVerificationService",
    ),
    "SuperTokensPasswordResetService": ("services.email", "SuperTokensPasswordResetService"),
}


def __getattr__(name: str):
    if name not in _EXPORT_MAP:
        raise AttributeError(f"module 'services' has no attribute {name}")

    module_name, attr_name = _EXPORT_MAP[name]
    module = import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value
