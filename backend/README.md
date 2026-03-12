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
| [aioboto3](https://aioboto3.readthedocs.io/) | Almacenamiento de archivos (S3-compatible) |
| [Logfire](https://logfire.pydantic.dev/) | Observabilidad y trazas |
| [SlowAPI](https://slowapi.readthedocs.io/) | Rate limiting |
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

---

## Requisitos previos

- Python **3.12+**
- [uv](https://github.com/astral-sh/uv) (gestor de paquetes)
- Docker & Docker Compose (para ejecución en contenedores)
- PostgreSQL accesible (local o remoto)

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
WEBSITE_DOMAIN=https://example.com
FOOTER_MESSAGE=Gracias por su preferencia.

# Logfire
LOGFIRE_TOKEN=your_logfire_token

# CORS
ALLOWED_ORIGINS=["https://example.com"]
ALLOW_METHODS=["GET","POST","PUT","PATCH","DELETE","OPTIONS"]
```

> En entorno `dev`, las variables de SMTP se sobreescriben automáticamente para apuntar a **Mailhog**.

---

## Instalación y ejecución

### Desarrollo (Docker)

```bash
cd backend/docker
docker compose -f docker-compose.dev.yml up --build
```

Incluye:
- **API** con hot-reload (`uvicorn --reload`)
- **SuperTokens** con PostgreSQL
- **Mailhog** para captura local de correos (UI en `http://localhost:8025`)

### Producción (Docker)

```bash
cd backend/docker
docker compose -f docker-compose.prod.yml up --build -d
```

Ejecuta las migraciones automáticamente antes de iniciar el servidor con **Gunicorn + UvicornWorker** (4 workers).

### Local sin Docker

```bash
# Instalar dependencias
uv sync

# Activar entorno virtual
source .venv/bin/activate

# Iniciar servidor
uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

---

## Migraciones de base de datos

```bash
# Generar una nueva migración
alembic -c src/db/alembic.ini revision --autogenerate -m "descripción"

# Aplicar migraciones pendientes
alembic -c src/db/alembic.ini upgrade head

# Revertir última migración
alembic -c src/db/alembic.ini downgrade -1
```

---

## Autenticación y roles

La autenticación está gestionada por **SuperTokens** con soporte para:

- **Email + contraseña** (con campos personalizados: `documentid`, `phone`, `first_name`, `last_name`, `birth_date`)
- **Google OAuth**
- **Verificación de correo** obligatoria (`REQUIRED`)
- **Account linking** automático

Cada endpoint está protegido con `require_scope("recurso:accion")`, que valida:
1. Sesión activa de SuperTokens
2. Permiso (`PermissionClaim`) en el token
3. Email verificado
4. Empleado registrado en la base de datos

**Ejemplo de scopes disponibles:**

| Scope | Descripción |
|---|---|
| `clients:read` | Leer clientes |
| `clients:write` | Crear/editar/eliminar clientes |
| `catalog:read` | Leer productos y servicios |
| `catalog:write` | Gestionar catálogo |
| `orders:read` / `orders:write` | Gestión de pedidos |
| `inventory:write` | Actualizar inventario |
| `invoices:write` | Generar facturas |
| `employees:self:write` | El empleado puede editar su propio perfil |

Los roles y permisos se administran desde el **SuperTokens Dashboard** (`/auth/dashboard`).

---

## Endpoints principales

La API está disponible bajo el prefijo `/v1`. Documentación interactiva disponible en `/docs` (solo entornos no productivos).

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/client/` | Crear cliente |
| `GET` | `/client/{id}` | Obtener cliente por ID |
| `GET` | `/client/` | Listar clientes (paginado) |
| `POST` | `/product/` | Crear producto |
| `GET` | `/product/low-stock` | Productos con stock bajo |
| `GET` | `/product/expired` | Productos vencidos |
| `PATCH` | `/product/image/{id}` | Actualizar imagen de producto |
| `POST` | `/service/` | Crear servicio |
| `POST` | `/order/` | Crear pedido |
| `POST` | `/order/product` | Agregar producto a pedido |
| `PATCH` | `/order/{id}/inventory` | Descontar inventario del pedido |
| `POST` | `/payment/` | Registrar pago |
| `POST` | `/invoice/generate` | Generar y enviar factura PDF |
| `GET` | `/files/{key}` | Obtener archivo del storage |
| `GET` | `/employee/employee/profile/complete` | Completar perfil de empleado |

Rate limiting global: **120 req/min** sostenido, **30 req/s** en picos.

---

## Estructura del proyecto

```
backend/
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.dev.yml
│   └── docker-compose.prod.yml
├── src/
│   ├── api/v1/routes/       # Endpoints FastAPI
│   ├── core/                # Config, auth, errores, storage, logging
│   ├── db/                  # Engine, sesiones, migraciones Alembic
│   ├── middlewares/         # Logging de requests
│   ├── models/              # Tablas SQLModel
│   ├── repositories/        # Capa de acceso a datos
│   ├── schemas/             # Esquemas Pydantic (Create/Read/Update)
│   ├── services/            # Lógica de negocio
│   ├── templates/           # Plantillas HTML (emails, facturas)
│   ├── utils/               # Utilidades (upload de imágenes, etc.)
│   └── main.py              # Punto de entrada de la aplicación
├── tests/
├── pyproject.toml
└── .python-version
```

---

## Tests

```bash
pytest tests/
```

> Los tests se encuentran en desarrollo. Actualmente existe un test dummy de ejemplo.
