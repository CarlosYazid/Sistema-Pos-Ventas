# Backend — Sistema POS de Ventas

API REST para un sistema de punto de venta (POS) construida con **FastAPI**, **SQLModel** y **SuperTokens**.

---

## Tabla de contenidos

- [Tecnologías](#tecnologías)
- [Arquitectura](#arquitectura)
- [Requisitos previos](#requisitos-previos)
- [Variables de entorno](#variables-de-entorno)
- [Instalación y ejecución](#instalación-y-ejecución)
  - [Desarrollo (Docker)](#desarrollo-docker)
  - [Producción (Docker)](#producción-docker)
  - [Local sin Docker](#local-sin-docker)
- [Migraciones de base de datos](#migraciones-de-base-de-datos)
- [Autenticación y roles](#autenticación-y-roles)
- [Endpoints principales](#endpoints-principales)
- [Facturación](#facturación)
- [Alertas de inventario](#alertas-de-inventario)
- [Workers y tareas en segundo plano](#workers-y-tareas-en-segundo-plano)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Tests](#tests)

---

## Tecnologías

| Herramienta | Uso |
|---|---|
| [FastAPI](https://fastapi.tiangolo.com/) | Framework web |
| [SQLModel](https://sqlmodel.tiangolo.com/) | ORM + validación |
| [Alembic](https://alembic.sqlalchemy.org/) | Migraciones de base de datos |
| [PostgreSQL](https://www.postgresql.org/) | Base de datos principal |
| [SuperTokens](https://supertokens.com/) | Autenticación y gestión de sesiones |
| [Celery](https://docs.celeryq.dev/) | Cola de tareas asíncronas |
| [Redis](https://redis.io/) | Broker y backend para Celery |
| [aioboto3](https://aioboto3.readthedocs.io/) | Almacenamiento de archivos (S3-compatible) |
| [Logfire](https://logfire.pydantic.dev/) | Observabilidad y trazas |
| [WeasyPrint](https://weasyprint.org/) | Generación de facturas en PDF |
| [FastAPI-Mail](https://sabuhish.github.io/fastapi-mail/) | Envío de correos electrónicos |
| [uv](https://github.com/astral-sh/uv) | Gestión de dependencias |

---

## Arquitectura

El proyecto sigue una arquitectura en capas:

```
API Routes → Services → Repositories → Models (SQLModel)
```

- **`api/`** — Rutas HTTP organizadas por recurso (v1).
- **`services/`** — Lógica de negocio. Cada servicio coordina operaciones sobre uno o más repositorios.
- **`repositories/`** — Acceso a datos. Abstracciones reutilizables sobre SQLModel/SQLAlchemy.
- **`models/`** — Definición de tablas y relaciones.
- **`schemas/`** — Esquemas Pydantic para validación de entrada/salida.
- **`core/`** — Configuración global, autenticación, manejo de errores, logging y rate limiting.
- **`db/`** — Inicialización del engine, sesiones y migraciones Alembic.
- **`tasks/`** — Tareas Celery: generación de facturas PDF y alertas de inventario por cron.

---

## Requisitos previos

- Python **3.13+**
- [uv](https://github.com/astral-sh/uv) (gestor de paquetes)
- Docker & Docker Compose (para ejecución en contenedores)
- PostgreSQL accesible (local o remoto)
- Redis accesible (local o remoto)

---

## Variables de entorno

Crea un archivo `.env` en la raíz del repositorio. A continuación las variables requeridas:

```env
# General
APP_NAME=SalesApp
HOST=0.0.0.0
PORT=8080
ENVIRONMENT=dev   # dev | prod | stag

# Base de datos
DB_URL_SYNC=postgresql://user:pass@localhost:5432/dbname
DB_URL_ASYNC=postgresql+asyncpg://user:pass@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=change-me

# SuperTokens
SUPERTOKENS_HOST=http://localhost
SUPERTOKENS_PORT=3567
SUPERTOKENS_DB_URI=postgresql://user:pass@localhost:5432/supertokens
DASHBOARD_API_KEY=your_dashboard_key
DEFAULT_ROLE=employee

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Almacenamiento (S3-compatible, ej. Cloudflare R2)
STORAGE_ENDPOINT_URL=https://your-endpoint.r2.cloudflarestorage.com
STORAGE_ACCESS_KEY=your_access_key
STORAGE_SECRET_KEY=your_secret_key
STORAGE_REGION=auto
BUCKET_NAME=your_bucket
IMAGE_FOLDER=images
INVOICE_FOLDER=invoices

# Email (SMTP)
SMTP_USER=noreply@example.com
SMTP_PASS=your_smtp_password
SMTP_SERVER=smtp.example.com
SMTP_PORT=587

# Empresa
COMPANY_NAME=Mi Empresa
COMPANY_EMAIL=info@example.com
COMPANY_PHONE=+57 300 000 0000
COMPANY_ADDRESS=Calle 123, Ciudad
COMPANY_LOGO=https://...
WEBSITE_DOMAIN=https://example.com
INVENTORY_URL=https://example.com/inventory
FOOTER_MESSAGE=Gracias por su preferencia.

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_BACKEND_URL=redis://localhost:6379/1
REDIS_PASSWORD=your_redis_password

# Cron jobs
CRON_HOUR_LOW_STOCK_ALERTS=8
CRON_HOUR_EXPIRED_ALERTS=8

# Workers (opcionales, con valores por defecto)
CONCURRENCY_INVOICES=2
CONCURRENCY_CRON=1
MAX_TASKS_PER_CHILD_INVOICES=50
MAX_TASKS_PER_CHILD_CRON=200
CELERY_LOGLEVEL=info

# Logfire
LOGFIRE_TOKEN=your_logfire_token

# CORS
ALLOWED_ORIGINS=["https://example.com"]
ALLOW_METHODS=["GET","POST","PUT","PATCH","DELETE","OPTIONS"]
```

> En entorno `dev`, las variables de SMTP se sobreescriben automáticamente para apuntar a **Mailhog** y los CORS se abren a `*`.

---

## Instalación y ejecución

### Desarrollo (Docker)

```bash
cd backend/docker
docker compose -f docker-compose.dev.yml up --build
```

Incluye:
- **API** con hot-reload (`python src/main.py`)
- **SuperTokens** con PostgreSQL
- **Redis** con autenticación y persistencia
- **Mailhog** para captura local de correos (UI en `http://localhost:8025`)
- **Worker de facturas** (`worker-invoices`) — cola `invoices`
- **Worker de cron** (`worker-cron`) — cola `cron`
- **Beat** (scheduler de tareas periódicas)

### Producción (Docker)

```bash
cd backend/docker
docker compose -f docker-compose.prod.yml up --build -d
```

Ejecuta las migraciones automáticamente antes de iniciar el servidor con **Gunicorn + UvicornWorker** (4 workers). Incluye los mismos workers y beat que el entorno de desarrollo.

### Local sin Docker

```bash
# Instalar dependencias
uv sync

# Activar entorno virtual
source .venv/bin/activate

# Iniciar servidor
uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload

# Iniciar worker de facturas (en otra terminal)
celery -A src.celery_app worker -Q invoices -n invoices.%h --concurrency=2 --loglevel=info

# Iniciar worker de cron (en otra terminal)
celery -A src.celery_app worker -Q cron -n cron.%h --concurrency=1 --loglevel=info

# Iniciar beat scheduler (en otra terminal)
celery -A src.celery_app beat --loglevel=info
```

---

## Migraciones de base de datos

```bash
# Generar una nueva migración
alembic -c alembic.ini revision --autogenerate -m "descripción"

# Aplicar migraciones pendientes
alembic -c alembic.ini upgrade head

# Revertir última migración
alembic -c alembic.ini downgrade -1
```

### Historial de migraciones relevantes

| Revisión | Descripción |
|---|---|
| `da86bf9f5b9c` | Migración inicial (tablas base) |
| `18a348046803` | Índices únicos en `client` y `employee` |
| `633c72a87f5a` | Corrección de cascadas en `product_category` |
| `ae18940c7534` | Cascade delete en `order_products` y `order_services` |
| `ee6e7a2f2b56` | Cascade delete en `service_inputs` |
| `96d4ea3425d7` | Cascade delete en `payments` al eliminar cliente |
| `09dd04194263` | Columna `is_verified` en `employee` |
| `c7dd19dc2cb9` | Tabla `employee` refactorizada: `user_id`, `profile_completed`; eliminados `password`, `provider`, `provider_id` |
| `4f8d3ea302c1` | Eliminación de columna `role` de `employee` (gestionado por SuperTokens) |
| `8dca16f2058f` | Eliminación de columna `is_verified` de `employee` |
| `f8c2b0b4b3e1` | Campos `verification_token` y `pdf_key` en `order` para facturación |
| `de13bc3d81ac` | Nuevas tablas `StockAlert` y `ExpirationAlert` con índices parciales |
| `df11857276e9` | Triggers PostgreSQL para creación automática de alertas de stock y vencimiento |

---

## Autenticación y roles

La autenticación está gestionada por **SuperTokens** con soporte para:

- **Email + contraseña** (con campos personalizados: `documentid`, `phone`, `first_name`, `last_name`, `birth_date`)
- **Google OAuth**
- **Verificación de correo** obligatoria (`REQUIRED`)
- **Account linking** automático entre proveedores

Al registrarse, el sistema crea automáticamente un registro de `Employee` en la base de datos y asigna el rol definido en `DEFAULT_ROLE` (por defecto `employee`) vía SuperTokens.

Cada endpoint está protegido con `require_scope("recurso:accion")`, que valida:
1. Sesión activa de SuperTokens
2. Permiso (`PermissionClaim`) en el token
3. Email verificado
4. Empleado registrado en la base de datos

### Scopes disponibles

| Scope | Descripción |
|---|---|
| `clients:read` | Leer clientes individuales |
| `clients:write` | Crear/editar/eliminar clientes |
| `clients:all:read` | Listar todos los clientes |
| `employees:read` | Leer empleados individuales |
| `employees:write` | Crear y eliminar empleados |
| `employees:self:write` | El empleado puede editar su propio perfil |
| `employees:all:read` | Listar todos los empleados |
| `catalog:read` | Leer productos, servicios y categorías |
| `catalog:write` | Gestionar catálogo completo |
| `catalog:all:read` | Listar todo el catálogo |
| `orders:read` | Leer pedidos individuales |
| `orders:write` | Crear, editar y gestionar pedidos |
| `orders:all:read` | Listar todos los pedidos |
| `inventory:write` | Descontar stock al confirmar pedido |
| `payments:read` | Leer pagos individuales |
| `payments:write` | Crear, editar y eliminar pagos |
| `invoices:write` | Generar y enviar facturas |
| `files:read` | Descargar archivos del storage |
| `task:read` | Consultar estado de tareas Celery |

Los roles y permisos se administran desde el **SuperTokens Dashboard** en `/auth/dashboard`.

---

## Endpoints principales

La API está disponible bajo el prefijo `/v1`. Documentación interactiva en `/docs` (solo entornos no productivos).

### Clientes (`/client`)

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/client/` | Crear cliente |
| `GET` | `/client/{id}` | Obtener cliente por ID |
| `PATCH` | `/client/` | Actualizar cliente |
| `DELETE` | `/client/{id}` | Eliminar cliente |
| `GET` | `/client/` | Listar clientes (paginado) |

### Empleados (`/employee`)

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/employee/` | Crear empleado |
| `GET` | `/employee/{id}` | Obtener empleado por ID |
| `GET` | `/employee/me` | Obtener perfil del empleado autenticado |
| `PATCH` | `/employee/` | Actualizar empleado |
| `PATCH` | `/employee/me/complete` | Completar perfil de onboarding |
| `PATCH` | `/employee/me/change-email` | Cambiar email (actualiza SuperTokens y DB) |
| `PATCH` | `/employee/me/change-password` | Cambiar contraseña (revoca todas las sesiones) |
| `DELETE` | `/employee/{id}` | Eliminar empleado |
| `GET` | `/employee/` | Listar empleados (paginado) |

### Productos y Catálogo (`/product`, `/service`)

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/product/` | Crear producto |
| `GET` | `/product/{id}` | Obtener producto |
| `PATCH` | `/product/` | Actualizar producto |
| `PATCH` | `/product/image/{id}` | Actualizar imagen de producto |
| `DELETE` | `/product/{id}` | Eliminar producto |
| `GET` | `/product/` | Listar productos (paginado) |
| `GET` | `/product/low-stock` | Productos con stock bajo o igual al mínimo |
| `GET` | `/product/expired` | Productos vencidos |
| `POST` | `/product/category` | Crear categoría |
| `POST` | `/product/product-category` | Asociar producto a categoría |
| `DELETE` | `/product/product-category` | Desasociar producto de categoría |
| `POST` | `/service/` | Crear servicio |
| `GET` | `/service/{id}` | Obtener servicio |
| `PATCH` | `/service/` | Actualizar servicio |
| `DELETE` | `/service/{id}` | Eliminar servicio |
| `GET` | `/service/` | Listar servicios (paginado) |
| `POST` | `/service/service-input` | Agregar insumo a servicio |
| `DELETE` | `/service/service-input` | Remover insumo de servicio |

### Pedidos (`/order`)

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/order/` | Crear pedido |
| `GET` | `/order/{id}` | Obtener pedido |
| `PATCH` | `/order/` | Actualizar pedido |
| `DELETE` | `/order/{id}` | Eliminar pedido |
| `GET` | `/order/` | Listar pedidos (paginado) |
| `POST` | `/order/product` | Agregar producto a pedido |
| `PATCH` | `/order/product` | Actualizar cantidad de producto en pedido |
| `DELETE` | `/order/product` | Remover producto de pedido |
| `POST` | `/order/service` | Agregar servicio a pedido |
| `PATCH` | `/order/service` | Actualizar cantidad de servicio en pedido |
| `DELETE` | `/order/service` | Remover servicio de pedido |
| `PATCH` | `/order/{id}/inventory` | Descontar inventario y calcular total |
| `POST` | `/order/{id}/invoice` | Generar token y encolar tarea de factura |
| `GET` | `/order/verify/{token}` | Obtener factura PDF por token de verificación |

### Pagos (`/payment`)

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/payment/` | Registrar pago |
| `GET` | `/payment/{id}` | Obtener pago |
| `PATCH` | `/payment/` | Actualizar pago |
| `DELETE` | `/payment/{id}` | Eliminar pago |

### Archivos y Tareas

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/files/{key}` | Obtener archivo del storage por clave |
| `GET` | `/tasks/{task_id}` | Consultar estado de tarea Celery |

---

## Facturación

El flujo de facturación es asíncrono y usa Celery + WeasyPrint:

1. **`POST /v1/order/{order_id}/invoice`** — Valida que el pedido exista, crea el token de verificación firmado con HMAC-SHA256 y encola la tarea `generate_invoice` en la cola `invoices`.
2. **Worker** (`worker-invoices`) procesa la tarea: genera el HTML con Jinja2, lo convierte a PDF con WeasyPrint, sube el PDF al storage S3-compatible, guarda `verification_token` y `pdf_key` en la orden, y envía el email con el enlace al cliente.
3. **`GET /v1/order/verify/{verification_token}`** — Valida la firma del token, busca la orden asociada y retorna el PDF directamente desde el storage (`Content-Disposition: inline`).
4. **`GET /v1/tasks/{task_id}`** — Permite consultar el estado de la tarea encolada.

### Notas importantes

- El `verification_token` se crea **antes** del render para mantener el PDF inmutable.
- La firma usa `SECRET_KEY` con HMAC-SHA256 en formato `token.firma_base64url`.
- El QR code se genera en el worker e incrusta en el HTML como data URL base64.
- La generación PDF ocurre **solo en el worker**, nunca en endpoints async.
- Si el pedido está en estado `PENDING` o `CANCELLED`, la tarea retorna sin generar el PDF.
- Si el pedido ya tiene `verification_token`, se retorna la URL existente sin regenerar.

### Ejecutar worker de facturas

```bash
celery -A src.celery_app worker -Q invoices -n invoices.%h --concurrency=2 --loglevel=info --max-tasks-per-child=50
```

Se recomienda `--concurrency=2` como máximo porque WeasyPrint consume CPU y RAM. En producción ajustar según los recursos disponibles.

---

## Alertas de inventario

El sistema genera alertas automáticas mediante **triggers de PostgreSQL** y las procesa con **tareas Celery periódicas**.

### Triggers de base de datos

- **`trg_insert_stock_alert`** — Se activa al actualizar `stock` en la tabla `product`. Si `stock <= minimum_stock`, inserta un registro en `StockAlert`.
- **`trg_check_expiration`** — Se activa al insertar o actualizar un `product`. Si `expiration_date <= CURRENT_DATE + 7 días`, inserta un registro en `ExpirationAlert`.

Ambos usan `ON CONFLICT DO NOTHING` para evitar duplicados.

### Tareas cron (Celery Beat)

| Tarea | Cola | Horario | Descripción |
|---|---|---|---|
| `low_stock_alerts` | `cron` | `CRON_HOUR_LOW_STOCK_ALERTS:00` | Envía email con productos de stock bajo no notificados y los marca como `notified=True` |
| `expired_alerts` | `cron` | `CRON_HOUR_EXPIRED_ALERTS:00` | Envía email con productos vencidos no notificados y los marca como `notified=True` |

La zona horaria del scheduler es `America/Bogota`.

### Ejecutar worker de cron

```bash
celery -A src.celery_app worker -Q cron -n cron.%h --concurrency=1 --loglevel=info --max-tasks-per-child=200

# Beat scheduler (en proceso separado)
celery -A src.celery_app beat --loglevel=info --pidfile=/tmp/celerybeat.pid
```

---

## Workers y tareas en segundo plano

### Colas disponibles

| Cola | Worker | Tareas |
|---|---|---|
| `invoices` | `worker-invoices` | `generate_invoice` |
| `cron` | `worker-cron` | `low_stock_alerts`, `expired_alerts` |

### Configuración de Celery

| Parámetro | Valor |
|---|---|
| Serialización | JSON |
| `task_acks_late` | `True` (garantía de entrega) |
| `task_reject_on_worker_lost` | `True` |
| `task_time_limit` | 300 s |
| `task_soft_time_limit` | 240 s |
| `task_max_retries` | 3 |
| `task_default_retry_delay` | 30 s |
| `worker_prefetch_multiplier` | 1 |
| `result_expires` | 3600 s |

En desarrollo, SMTP se redirige a Mailhog (UI en `http://localhost:8025`).

---

## Estructura del proyecto

```
backend/
├── docker/
│   ├── Dockerfile               # Multi-stage: api-dev, api-prod, back-task-dev, back-task-prod
│   ├── docker-compose.dev.yml
│   └── docker-compose.prod.yml
├── migrations/
│   ├── env.py
│   └── versions/                # Historial de migraciones Alembic
├── src/
│   ├── api/v1/routes/           # Endpoints FastAPI por recurso
│   │   ├── client.py
│   │   ├── employee.py
│   │   ├── files.py
│   │   ├── order.py             # Incluye facturación y verificación
│   │   ├── others.py            # Estado de tareas Celery
│   │   ├── payment.py
│   │   ├── product.py
│   │   └── service.py
│   ├── celery_app.py            # Configuración de Celery, colas y beat schedule
│   ├── core/                    # Config, auth (SuperTokens), errores, storage, observabilidad
│   ├── db.py                    # Engine async, sesiones, init/close
│   ├── middlewares/             # Logging de requests con Logfire
│   ├── models/                  # Tablas SQLModel
│   │   ├── alert.py             # StockAlert, ExpirationAlert
│   │   ├── client.py
│   │   ├── employee.py          # user_id, profile_completed (sin password/role)
│   │   ├── order.py             # verification_token, pdf_key
│   │   ├── payment.py
│   │   ├── product.py
│   │   └── service.py
│   ├── repositories/            # Capa de acceso a datos
│   ├── schemas/                 # Esquemas Pydantic (Create/Read/Update)
│   ├── services/                # Lógica de negocio
│   │   ├── invoice.py           # Creación de token + encolar tarea + verificación PDF
│   │   └── ...
│   ├── tasks/
│   │   ├── invoices.py          # generate_invoice (WeasyPrint + storage + email)
│   │   └── cron.py              # low_stock_alerts, expired_alerts
│   ├── templates/
│   │   ├── email/               # Plantillas HTML para emails
│   │   └── invoice.html         # Plantilla de factura PDF
│   ├── utils/
│   │   ├── order.py             # HMAC signing, QR generation, upload de PDFs
│   │   └── product.py           # Upload/delete de imágenes en storage
│   └── main.py                  # Punto de entrada FastAPI
├── tests/
│   ├── test_dummy.py
│   ├── test_generate_invoice_task.py
│   ├── test_signer.py           # Tests de firma HMAC de tokens
│   └── test_verify_endpoint.py  # Tests de endpoint de verificación de facturas
├── alembic.ini
├── pyproject.toml
├── redis.conf
└── .python-version              # Python 3.13
```

---

## Tests

```bash
pytest tests/
```

Los tests cubren:
- `test_dummy.py` — Test de sanity check básico.
- `test_signer.py` — Firma, verificación y detección de tokens manipulados con HMAC-SHA256.
- `test_generate_invoice_task.py` — Ejecución en seco de la tarea Celery de generación de facturas con mocks.
- `test_verify_endpoint.py` — Endpoint de verificación de facturas con SQLite en memoria; cubre token válido (200 + PDF) y token inválido (403).
