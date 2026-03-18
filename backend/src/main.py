from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination
from supertokens_python import get_all_cors_headers
from supertokens_python import init as init_supertokens
from supertokens_python.framework.fastapi import get_middleware
from uvicorn import run

from api import Router
from core.auth import (
    APP_INFO,
    SUPERTOKENS_CONFIG,
    build_recipe_list,
)
from core.errors import (
    ERROR_STATUS_CODE,
    ApplicationError,
)
from core.observability import setup_observability
from core.settings import (
    SETTINGS,
    Environment,
)
from db import close_engine, init_db, init_engine
from middlewares import LoggingContextMiddleware
from services.email import EmailService

EMAILSERVICE = EmailService(SETTINGS.email_conf)

init_supertokens(
    app_info=APP_INFO,
    supertokens_config=SUPERTOKENS_CONFIG,
    framework="fastapi",
    recipe_list=build_recipe_list(EMAILSERVICE),
    mode="asgi" if SETTINGS.environment != Environment.PRODUCTION else "wsgi",
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    setup_observability(SETTINGS.app_name, app)

    init_engine()

    if SETTINGS.environment == Environment.DEVELOPMENT:
        await init_db()

    yield

    await close_engine()


app = FastAPI(
    title=SETTINGS.app_name,
    description=SETTINGS.description,
    version=SETTINGS.version,
    lifespan=lifespan,
    docs_url=None if SETTINGS.environment == Environment.PRODUCTION else "/docs",
    redoc_url=None if SETTINGS.environment == Environment.PRODUCTION else "/redoc",
    openapi_url=None if SETTINGS.environment == Environment.PRODUCTION else "/openapi.json",
)


@app.exception_handler(ApplicationError)
def application_error_handler(request: Request, exc: ApplicationError):
    return JSONResponse(
        status_code=ERROR_STATUS_CODE.get(type(exc), 500),
        content={"detail": exc.message},
    )


add_pagination(app)

app.add_middleware(get_middleware())
app.add_middleware(
    CORSMiddleware,
    allow_origins=SETTINGS.allowed_origins,
    allow_credentials=SETTINGS.allow_credentials,
    allow_methods=SETTINGS.allow_methods,
    allow_headers=["Content-Type", *get_all_cors_headers()],
)
app.add_middleware(LoggingContextMiddleware)

app.include_router(Router)


@app.get("/")
async def root():
    return {"api": SETTINGS.app_name, "version": SETTINGS.version, "status": "Ok"}


if __name__ == "__main__":
    run("main:app", host=SETTINGS.host, port=SETTINGS.port, reload=True)
