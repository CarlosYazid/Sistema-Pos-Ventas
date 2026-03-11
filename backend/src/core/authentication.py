from typing import Any

import logfire
from supertokens_python import InputAppInfo, SupertokensConfig
from supertokens_python.ingredients.emaildelivery.types import EmailDeliveryConfig
from supertokens_python.recipe import (
    dashboard,
    emailpassword,
    emailverification,
    session,
    thirdparty,
    userroles,
)
from supertokens_python.recipe.emailpassword import EmailPasswordOverrideConfig
from supertokens_python.recipe.emailpassword.interfaces import (
    APIInterface as EmailPasswordAPIInterface,
)
from supertokens_python.recipe.emailpassword.interfaces import SignUpPostOkResult
from supertokens_python.recipe.thirdparty import (
    ProviderClientConfig,
    ProviderConfig,
    ProviderInput,
    SignInAndUpFeature,
    ThirdPartyOverrideConfig,
)
from supertokens_python.recipe.thirdparty.interfaces import (
    APIInterface as ThirdPartyAPIInterface,
)
from supertokens_python.recipe.thirdparty.interfaces import SignInUpPostOkResult
from supertokens_python.recipe.userroles.asyncio import (
    add_role_to_user,
)
from supertokens_python.recipe.userroles.interfaces import UnknownRoleError

from db import main as db_main
from services import EmployeeService
from services.email import (
    EmailService,
    SuperTokensEmailVerificationService,
    SuperTokensPasswordResetService,
)

from .settings import SETTINGS

EMPLOYEE_SERVICE = EmployeeService()

SUPERTOKENS_CONFIG = SupertokensConfig(connection_uri=SETTINGS.supertokens_url)

APP_INFO = InputAppInfo(
    app_name=SETTINGS.app_name,
    api_domain=f"{SETTINGS.host}:{SETTINGS.port}",
    website_domain=SETTINGS.website_domain,
    api_base_path="/auth",
    website_base_path="/auth",
)


async def _assign_default_role(user_id: str) -> None:
    result = await add_role_to_user(
        tenant_id=SETTINGS.tenant_id,
        user_id=user_id,
        role=SETTINGS.default_role,
    )

    if isinstance(result, UnknownRoleError):
        logfire.warning(
            "default employee role is not defined in supertokens",
            user_id=user_id,
            role=SETTINGS.default_role,
        )


async def _sync_employee_identity(user_id: str, email: str) -> None:
    if db_main.AsyncSessionLocal is None:
        logfire.warning(
            "cannot sync employee identity because sessionmaker is not initialized",
            user_id=user_id,
            email=email,
        )
        return

    async with db_main.AsyncSessionLocal() as db_session:
        await EMPLOYEE_SERVICE.sync_identity_by_user_id(
            user_id=user_id,
            email=email,
            session=db_session,
        )

    await _assign_default_role(user_id)


def override_emailpassword_apis(
    original_implementation: EmailPasswordAPIInterface,
) -> EmailPasswordAPIInterface:
    original_sign_up_post = original_implementation.sign_up_post

    async def sign_up_post(*args: Any, **kwargs: Any):
        result = await original_sign_up_post(*args, **kwargs)

        if isinstance(result, SignUpPostOkResult):
            user_id = result.user.id
            email = result.user.emails[0] if result.user.emails else None

            if email is not None:
                try:
                    await _sync_employee_identity(user_id=user_id, email=email)
                except Exception as exc:
                    logfire.error(
                        "failed syncing employee after emailpassword signup",
                        user_id=user_id,
                        email=email,
                        error=str(exc),
                    )

        return result

    original_implementation.sign_up_post = sign_up_post

    return original_implementation


def override_thirdparty_apis(
    original_implementation: ThirdPartyAPIInterface,
) -> ThirdPartyAPIInterface:
    original_sign_in_up_post = original_implementation.sign_in_up_post

    async def sign_in_up_post(*args: Any, **kwargs: Any):
        result = await original_sign_in_up_post(*args, **kwargs)

        if isinstance(result, SignInUpPostOkResult):
            user_id = result.user.id
            email = result.user.emails[0] if result.user.emails else None

            if email is not None:
                try:
                    await _sync_employee_identity(user_id=user_id, email=email)
                except Exception as exc:
                    logfire.error(
                        "failed syncing employee after thirdparty sign-in-up",
                        user_id=user_id,
                        email=email,
                        error=str(exc),
                    )

        return result

    original_implementation.sign_in_up_post = sign_in_up_post
    return original_implementation


def build_recipe_list(email_service: EmailService) -> list:
    return [
        session.init(),
        userroles.init(),
        dashboard.init(api_key=SETTINGS.dashboard_api_key),
        thirdparty.init(
            sign_in_and_up_feature=SignInAndUpFeature(
                providers=[
                    ProviderInput(
                        config=ProviderConfig(
                            third_party_id="google",
                            clients=[
                                ProviderClientConfig(
                                    client_id=SETTINGS.google_client_id,
                                    client_secret=SETTINGS.google_client_secret.get_secret_value(),
                                )
                            ],
                        )
                    )
                ]
            ),
            override=ThirdPartyOverrideConfig(apis=override_thirdparty_apis),
        ),
        emailpassword.init(
            override=EmailPasswordOverrideConfig(apis=override_emailpassword_apis),
            email_delivery=EmailDeliveryConfig(
                service=SuperTokensPasswordResetService(email_service),
            ),
        ),
        emailverification.init(
            mode="REQUIRED",
            email_delivery=EmailDeliveryConfig(
                service=SuperTokensEmailVerificationService(email_service),
            ),
        ),
    ]
