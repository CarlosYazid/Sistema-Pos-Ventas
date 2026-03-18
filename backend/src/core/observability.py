import logfire

from .settings import SETTINGS


def setup_observability(service_name=None, app=None):

    logfire.configure(
        service_name=SETTINGS.app_name if not service_name else service_name,
        environment=SETTINGS.environment,
        token=SETTINGS.logfire_token.get_secret_value(),
    )

    if app is not None:
        logfire.instrument_fastapi(app)

    logfire.instrument_sqlalchemy()
    logfire.instrument_celery(propagate=True)

    logfire.instrument_redis()
