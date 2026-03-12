import supertokens_python as supertokens
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from fastapi_querybuilder import QueryBuilder
from sqlmodel.ext.asyncio.session import AsyncSession
from supertokens_python.recipe.emailpassword.asyncio import (
    update_email_or_password,
    verify_credentials,
)
from supertokens_python.recipe.emailpassword.types import RecipeUserId
from supertokens_python.recipe.session.asyncio import revoke_all_sessions_for_user

from core import SETTINGS, require_scope
from db import get_session
from models import Employee
from schemas import (
    ChangePassword,
    EmployeeCreate,
    EmployeeProfileComplete,
    EmployeeRead,
    EmployeeUpdate,
)
from services import EmployeeService

router = APIRouter(prefix="/employee", tags=["Employee"])

EMPLOYEE_SERVICE = EmployeeService()


@router.post("/", response_model=EmployeeRead)
async def create_employee(
    employee: EmployeeCreate,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("employees:write")),
):

    return await EMPLOYEE_SERVICE.create(employee, session)


@router.get("/{employee_id}", response_model=EmployeeRead)
async def read_employee(
    employee_id: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("employees:read")),
):

    return await EMPLOYEE_SERVICE.read(employee_id, session)


@router.patch("/", response_model=EmployeeRead)
async def update_employee(
    fields: EmployeeUpdate,
    session: AsyncSession = Depends(get_session),
    current_employee: Employee = Depends(require_scope("employees:write")),
):

    return await EMPLOYEE_SERVICE.update(fields, session)


@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("employees:write")),
):
    return await EMPLOYEE_SERVICE.delete(employee_id, session)


@router.get("/", response_model=Page[EmployeeRead])
async def list_employees(
    query=QueryBuilder(Employee),
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("employees:read")),
):
    return await apaginate(session, query)


@router.get("/me", response_model=EmployeeRead)
async def read_me(current_employee: Employee = Depends(require_scope("employee:self:read"))):

    return current_employee


@router.patch("/me/complete", response_model=EmployeeRead)
async def complete_employee_profile(
    data: EmployeeProfileComplete,
    session: AsyncSession = Depends(get_session),
    current_employee: Employee = Depends(require_scope("employee:self:write")),
):

    if data.user_id != current_employee.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only complete your own employee profile.",
        )

    return await EMPLOYEE_SERVICE.complete_profile(data, current_employee, session)


@router.patch("/me/change-email", response_model=EmployeeRead)
async def change_email(
    email: str,
    session: AsyncSession = Depends(get_session),
    current_employee: Employee = Depends(require_scope("employee:self:write")),
):

    await update_email_or_password(
        recipe_user_id=RecipeUserId(current_employee.user_id), email=email
    )

    return await EMPLOYEE_SERVICE.update_email(email, current_employee, session)


@router.patch("/me/change-password")
async def change_password(
    fields: ChangePassword,
    current_employee: Employee = Depends(require_scope("employee:self:write")),
):

    user = await supertokens.get_user(current_employee.user_id)

    login_method = next(lm for lm in user.login_methods if lm.recipe_id == "emailpassword")

    if login_method is None:
        raise HTTPException(400, "User has no password")

    email = login_method.email

    result = await verify_credentials(
        tenant_id=SETTINGS.tenant_id, email=email, password=fields.old_password
    )

    if result.status != "OK":
        raise HTTPException(401, "Incorrect password")

    await update_email_or_password(
        recipe_user_id=RecipeUserId(current_employee.user_id), password=fields.new_password
    )

    await revoke_all_sessions_for_user(current_employee.user_id)

    return JSONResponse(
        content={
            "user_id": current_employee.user_id,
            "email": email,
        },
        status_code=200,
    )
