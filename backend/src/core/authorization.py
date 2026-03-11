from typing import Awaitable, Callable

from fastapi import Depends, HTTPException, status
from sqlmodel import select
from supertokens_python.recipe.emailverification import EmailVerificationClaim
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.userroles import PermissionClaim

from db import main as db_main
from models import Employee

Scope = str  # tipo alias claro


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
        # Aseguramos que la sesión de DB está inicializada
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
