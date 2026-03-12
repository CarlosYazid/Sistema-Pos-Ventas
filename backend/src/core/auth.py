from datetime import date
from typing import Any, Awaitable, Callable

import logfire
from fastapi import Depends, HTTPException, status
from sqlmodel import select
from supertokens_python import InputAppInfo, SupertokensConfig
from supertokens_python.ingredients.emaildelivery.types import EmailDeliveryConfig
from supertokens_python.recipe import (
    accountlinking,
    dashboard,
    emailpassword,
    emailverification,
    session,
    thirdparty,
    userroles,
)
from supertokens_python.recipe.emailpassword import EmailPasswordOverrideConfig, InputFormField
from supertokens_python.recipe.emailpassword.interfaces import (
    APIInterface as EmailPasswordAPIInterface,
)
from supertokens_python.recipe.emailpassword.interfaces import SignUpPostOkResult
from supertokens_python.recipe.emailverification import EmailVerificationClaim
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session
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
from supertokens_python.recipe.userroles import PermissionClaim
from supertokens_python.recipe.userroles.asyncio import (
    add_role_to_user,
)
from supertokens_python.recipe.userroles.interfaces import UnknownRoleError

from db import main as db_main
from models import Employee
from schemas import EmployeeCreate
from services import EmployeeService
from services.email import (
    EmailService,
    SuperTokensEmailVerificationService,
    SuperTokensPasswordResetService,
)

from .settings import SETTINGS

Scope = str

EMPLOYEE_SERVICE = EmployeeService()

SUPERTOKENS_CONFIG = SupertokensConfig(connection_uri=SETTINGS.supertokens_url)

APP_INFO = InputAppInfo(
    app_name=SETTINGS.app_name,
    api_domain=f"{SETTINGS.host}:{SETTINGS.port}",
    website_domain=SETTINGS.website_domain,
    api_base_path="/auth",
    website_base_path="/auth",
)


async def _create_employee(data: EmployeeCreate) -> None:
    if db_main.AsyncSessionLocal is None:
        logfire.warning(
            "cannot create employee because sessionmaker is not initialized",
            user_id=data.user_id,
            email=data.email,
        )
        return

    async with db_main.AsyncSessionLocal() as db_session:
        await EMPLOYEE_SERVICE.create(data, db_session)

    result = await add_role_to_user(
        tenant_id=SETTINGS.tenant_id, user_id=data.user_id, role=SETTINGS.default_role
    )

    if isinstance(result, UnknownRoleError):
        logfire.warning(
            "default employee role is not defined in supertokens",
            user_id=data.user_id,
            role=SETTINGS.default_role,
        )


def _override_emailpassword_apis(
    original_implementation: EmailPasswordAPIInterface,
) -> EmailPasswordAPIInterface:
    original_sign_up_post = original_implementation.sign_up_post

    async def sign_up_post(*args: Any, **kwargs: Any):
        result = await original_sign_up_post(*args, **kwargs)

        if isinstance(result, SignUpPostOkResult):
            form_data = {field.id: field.value for field in kwargs["form_fields"]}

            form_data["birth_date"] = date.fromisoformat(form_data["birth_date"])
            form_data["user_id"] = result.user.id
            form_data["email"] = result.user.emails[0]
            form_data["profile_completed"] = True

            try:
                await _create_employee(EmployeeCreate(**form_data))

            except Exception as exc:
                logfire.error(
                    "failed syncing employee after emailpassword signup",
                    user_id=result.user.id,
                    email=result.user.emails[0],
                    error=str(exc),
                )

        return result

    original_implementation.sign_up_post = sign_up_post

    return original_implementation


def _override_thirdparty_apis(
    original_implementation: ThirdPartyAPIInterface,
) -> ThirdPartyAPIInterface:
    original_sign_in_up_post = original_implementation.sign_in_up_post

    async def sign_in_up_post(*args: Any, **kwargs: Any):
        result = await original_sign_in_up_post(*args, **kwargs)

        if isinstance(result, SignInUpPostOkResult) and result.created_new_user:
            user_id = result.user.id
            email = result.user.emails[0]

            try:
                await _create_employee(EmployeeCreate(user_id=user_id, email=email))

            except Exception as exc:
                logfire.error(
                    "failed create employee after thirdparty sign-in-up",
                    user_id=user_id,
                    email=email,
                    error=str(exc),
                )

        return result

    original_implementation.sign_in_up_post = sign_in_up_post

    return original_implementation


def require_scope(scope: Scope) -> Callable[..., Awaitable[Employee]]:
    """
    Devuelve una dependencia que:
    - verifica la sesión usando verify_session,
      overrideando los validators globales para añadir:
        * PermissionClaim.validators.includes(scope)
        * EmailVerificationClaim.validators.is_verified()
    - recupera el Employee asociado al user_id de la sesión
    - lanza HTTPException si no existe el empleado
    """

    async def dependency(
        session_container: SessionContainer = Depends(
            verify_session(
                override_global_claim_validators=lambda validators, session, ctx: (
                    validators
                    + [
                        PermissionClaim.validators.includes(scope),
                        EmailVerificationClaim.validators.is_verified(),
                    ]
                )
            )
        ),
    ) -> Employee:
        if getattr(db_main, "AsyncSessionLocal", None) is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database session is not initialized.",
            )

        user_id = session_container.get_user_id()

        async with db_main.AsyncSessionLocal() as session:
            result = await session.exec(select(Employee).where(Employee.user_id == user_id))
            employee = result.one_or_none()

        if employee is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The authenticated user is not linked to an employee account.",
            )

        return employee

    return dependency


def build_recipe_list(email_service: EmailService) -> list:
    return [
        session.init(),
        userroles.init(),
        dashboard.init(api_key=SETTINGS.dashboard_api_key),
        accountlinking.init(
            should_do_automatic_account_linking=lambda *_: {
                "shouldAutomaticallyLink": True,
                "shouldRequireVerification": True,
            }
        ),
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
            override=ThirdPartyOverrideConfig(apis=_override_thirdparty_apis),
        ),
        emailpassword.init(
            override=EmailPasswordOverrideConfig(apis=_override_emailpassword_apis),
            email_delivery=EmailDeliveryConfig(
                service=SuperTokensPasswordResetService(email_service),
            ),
            sign_up_feature=emailpassword.InputSignUpFeature(
                form_fields=[
                    InputFormField(id="email"),
                    InputFormField(id="password"),
                    InputFormField(id="documentid"),
                    InputFormField(id="phone", optional=True),
                    InputFormField(id="first_name"),
                    InputFormField(id="last_name"),
                    InputFormField(id="birth_date"),
                ]
            ),
        ),
        emailverification.init(
            mode="REQUIRED",
            email_delivery=EmailDeliveryConfig(
                service=SuperTokensEmailVerificationService(email_service),
            ),
        ),
    ]
