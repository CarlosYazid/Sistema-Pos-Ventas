# Scopes por Endpoint

Referencia completa de los permisos (scopes) requeridos por cada endpoint de la API v1.

> Todos los endpoints también exigen **sesión activa** y **email verificado** via SuperTokens.

---

## Índice

- [Client](#client)
- [Employee](#employee)
- [Product](#product)
- [Service](#service)
- [Order](#order)
- [Payment](#payment)
- [Invoice](#invoice)
- [Files](#files)

---

## Client

**Prefijo:** `/client`

| Método | Ruta | Scope | Descripción |
|--------|------|-------|-------------|
| `POST` | `/client/` | `clients:write` | Crear un cliente |
| `GET` | `/client/{client_id}` | `clients:read` | Obtener cliente por ID |
| `GET` | `/client/email/{email}` | `clients:read` | Obtener cliente por email |
| `GET` | `/client/documentid/{documentid}` | `clients:read` | Obtener cliente por documento |
| `PATCH` | `/client/` | `clients:write` | Actualizar cliente por ID |
| `PATCH` | `/client/email` | `clients:write` | Actualizar cliente por email |
| `PATCH` | `/client/documentid` | `clients:write` | Actualizar cliente por documento |
| `DELETE` | `/client/{client_id}` | `clients:write` | Eliminar cliente por ID |
| `DELETE` | `/client/email/{email}` | `clients:write` | Eliminar cliente por email |
| `DELETE` | `/client/documentid/{documentid}` | `clients:write` | Eliminar cliente por documento |
| `GET` | `/client/` | `clients:all:read` | Listar todos los clientes (paginado) |

---

## Employee

**Prefijo:** `/employee`

| Método | Ruta | Scope | Descripción |
|--------|------|-------|-------------|
| `POST` | `/employee/employee` | `employees:write` | Crear un empleado |
| `GET` | `/employee/employee/{employee_id}` | `employees:read` | Obtener empleado por ID |
| `GET` | `/employee/employee/email/{email}` | `employees:read` | Obtener empleado por email |
| `GET` | `/employee/employee/documentid/{documentid}` | `employees:read` | Obtener empleado por documento |
| `PATCH` | `/employee/employee` | `employees:self:write` | Actualizar empleado por ID (solo el propio) |
| `PATCH` | `/employee/employee/email` | `employees:self:write` | Actualizar empleado por email (solo el propio) |
| `PATCH` | `/employee/employee/documentid` | `employees:self:write` | Actualizar empleado por documento (solo el propio) |
| `PATCH` | `/employee/employee/profile/complete` | `employees:self:write` | Completar perfil de onboarding (solo el propio) |
| `DELETE` | `/employee/employee/{employee_id}` | `employees:write` | Eliminar empleado por ID |
| `DELETE` | `/employee/employee/email/{email}` | `employees:write` | Eliminar empleado por email |
| `DELETE` | `/employee/employee/documentid/{documentid}` | `employees:write` | Eliminar empleado por documento |
| `GET` | `/employee/employee` | `employees:all:read` | Listar todos los empleados (paginado) |

> **Nota:** Los endpoints con scope `employees:self:write` validan adicionalmente que el empleado autenticado solo pueda modificar su propio registro. Si el campo identificador no coincide con el del token, se devuelve `403 Forbidden`.

---

## Product

**Prefijo:** `/product`

| Método | Ruta | Scope | Descripción |
|--------|------|-------|-------------|
| `POST` | `/product/` | `catalog:write` | Crear un producto |
| `GET` | `/product/{product_id}` | `catalog:read` | Obtener producto por ID |
| `PATCH` | `/product/` | `catalog:write` | Actualizar producto |
| `PATCH` | `/product/image/{product_id}` | `catalog:write` | Actualizar imagen de un producto |
| `DELETE` | `/product/{product_id}` | `catalog:write` | Eliminar producto |
| `GET` | `/product/` | `catalog:all:read` | Listar todos los productos (paginado) |
| `POST` | `/product/product-category` | `catalog:write` | Agregar producto a una categoría |
| `DELETE` | `/product/product-category` | `catalog:write` | Remover producto de una categoría |
| `POST` | `/product/category` | `catalog:write` | Crear una categoría |
| `GET` | `/product/category/{category_id}` | `catalog:read` | Obtener categoría por ID |
| `PATCH` | `/product/category` | `catalog:write` | Actualizar categoría |
| `DELETE` | `/product/category/{category_id}` | `catalog:write` | Eliminar categoría |
| `GET` | `/product/category` | `catalog:all:read` | Listar todas las categorías (paginado) |
| `GET` | `/product/low-stock` | `catalog:read` | Listar productos con stock bajo o igual al mínimo |
| `GET` | `/product/expired` | `catalog:read` | Listar productos vencidos |

---

## Service

**Prefijo:** `/service`

| Método | Ruta | Scope | Descripción |
|--------|------|-------|-------------|
| `POST` | `/service/` | `catalog:write` | Crear un servicio |
| `GET` | `/service/{service_id}` | `catalog:read` | Obtener servicio por ID |
| `PATCH` | `/service/` | `catalog:write` | Actualizar servicio |
| `DELETE` | `/service/{service_id}` | `catalog:write` | Eliminar servicio |
| `POST` | `/service/service-input` | `catalog:write` | Agregar producto como insumo de un servicio |
| `DELETE` | `/service/service-input` | `catalog:write` | Remover insumo de un servicio |
| `GET` | `/service/` | `catalog:all:read` | Listar todos los servicios (paginado) |

---

## Order

**Prefijo:** `/order`

| Método | Ruta | Scope | Descripción |
|--------|------|-------|-------------|
| `POST` | `/order/` | `orders:write` | Crear un pedido |
| `GET` | `/order/{order_id}` | `orders:read` | Obtener pedido por ID |
| `PATCH` | `/order/` | `orders:write` | Actualizar pedido |
| `DELETE` | `/order/{order_id}` | `orders:write` | Eliminar pedido |
| `POST` | `/order/product` | `orders:write` | Agregar producto a un pedido |
| `PATCH` | `/order/product` | `orders:write` | Actualizar cantidad de producto en un pedido |
| `DELETE` | `/order/product` | `orders:write` | Remover producto de un pedido |
| `POST` | `/order/service` | `orders:write` | Agregar servicio a un pedido |
| `PATCH` | `/order/service` | `orders:write` | Actualizar cantidad de servicio en un pedido |
| `DELETE` | `/order/service` | `orders:write` | Remover servicio de un pedido |
| `GET` | `/order/` | `orders:all:read` | Listar todos los pedidos (paginado) |
| `PATCH` | `/order/{order_id}/inventory` | `inventory:write` | Descontar inventario y calcular total del pedido |

---

## Payment

**Prefijo:** `/payment`

| Método | Ruta | Scope | Descripción |
|--------|------|-------|-------------|
| `POST` | `/payment/` | `payments:write` | Registrar un pago |
| `GET` | `/payment/{payment_id}` | `payments:read` | Obtener pago por ID |
| `PATCH` | `/payment/` | `payments:write` | Actualizar pago |
| `DELETE` | `/payment/{payment_id}` | `payments:write` | Eliminar pago |

---

## Invoice

**Prefijo:** `/invoice`

| Método | Ruta | Scope | Descripción |
|--------|------|-------|-------------|
| `POST` | `/invoice/generate` | `invoices:write` | Generar factura PDF, enviarla por email y subirla al storage |

---

## Files

**Prefijo:** `/files`

| Método | Ruta | Scope | Descripción |
|--------|------|-------|-------------|
| `GET` | `/files/{key}` | `files:read` | Obtener un archivo del storage por su ruta/clave |

---

## Resumen de scopes

| Scope | Recursos que protege |
|-------|---------------------|
| `clients:read` | Lectura individual de clientes |
| `clients:write` | Creación, edición y eliminación de clientes |
| `clients:all:read` | Listado completo de clientes |
| `employees:read` | Lectura individual de empleados |
| `employees:write` | Creación y eliminación de empleados |
| `employees:self:write` | Edición del propio perfil de empleado |
| `employees:all:read` | Listado completo de empleados |
| `catalog:read` | Lectura de productos, servicios y categorías |
| `catalog:write` | Gestión completa del catálogo (productos, servicios, categorías, imágenes, insumos) |
| `catalog:all:read` | Listado completo de productos, servicios y categorías |
| `orders:read` | Lectura individual de pedidos |
| `orders:write` | Creación, edición, eliminación y gestión de ítems en pedidos |
| `orders:all:read` | Listado completo de pedidos |
| `inventory:write` | Descuento de stock al confirmar un pedido |
| `payments:read` | Lectura individual de pagos |
| `payments:write` | Creación, edición y eliminación de pagos |
| `invoices:write` | Generación y envío de facturas |
| `files:read` | Descarga de archivos del storage |
