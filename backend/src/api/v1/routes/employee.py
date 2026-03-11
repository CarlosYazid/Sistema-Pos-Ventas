from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from fastapi_querybuilder import QueryBuilder
from sqlmodel.ext.asyncio.session import AsyncSession

from core import require_scope
from db import get_session
from models import Employee
from schemas import EmployeeCreate, EmployeeProfileComplete, EmployeeRead, EmployeeUpdate
from services import EmployeeService

router = APIRouter(prefix="/employee", tags=["Employee"])

EMPLOYEE_SERVICE = EmployeeService()


@router.post("/employee", response_model=EmployeeRead)
async def create_employee(
    employee: EmployeeCreate,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("employees:write")),
):
    return await EMPLOYEE_SERVICE.create(employee, session)


@router.get("/employee/{employee_id}", response_model=EmployeeRead)
async def read_employee(
    employee_id: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("employees:read")),
):
    return await EMPLOYEE_SERVICE.read(employee_id, session)


@router.get("/employee/email/{email}", response_model=EmployeeRead)
async def read_employee_by_email(
    email: str,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("employees:read")),
):
    return await EMPLOYEE_SERVICE.read_by_email(email, session)


@router.get("/employee/documentid/{documentid}", response_model=EmployeeRead)
async def read_employee_by_documentid(
    documentid: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("employees:read")),
):
    return await EMPLOYEE_SERVICE.read_by_documentid(documentid, session)


@router.patch("/employee", response_model=EmployeeRead)
async def update_employee(
    fields: EmployeeUpdate,
    session: AsyncSession = Depends(get_session),
    current_employee: Employee = Depends(require_scope("employees:self:write")),
):
    if fields.id is not None and fields.id != current_employee.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own employee profile.",
        )

    return await EMPLOYEE_SERVICE.update(fields, session)


@router.patch("/employee/email", response_model=EmployeeRead)
async def update_employee_by_email(
    fields: EmployeeUpdate,
    session: AsyncSession = Depends(get_session),
    current_employee: Employee = Depends(require_scope("employees:self:write")),
):
    if fields.email is not None and fields.email.lower() != current_employee.email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own employee profile.",
        )

    return await EMPLOYEE_SERVICE.update_by_email(fields, session)


@router.patch("/employee/documentid", response_model=EmployeeRead)
async def update_employee_by_documentid(
    fields: EmployeeUpdate,
    session: AsyncSession = Depends(get_session),
    current_employee: Employee = Depends(require_scope("employees:self:write")),
):
    if fields.documentid is not None and fields.documentid != current_employee.documentid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own employee profile.",
        )

    return await EMPLOYEE_SERVICE.update_by_documentid(fields, session)


@router.patch("/employee/profile/complete", response_model=EmployeeRead)
async def complete_employee_profile(
    data: EmployeeProfileComplete,
    session: AsyncSession = Depends(get_session),
    current_employee: object = Depends(require_scope("employees:self:write")),
):
    if data.email.lower() != current_employee.email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only complete your own employee profile.",
        )

    return await EMPLOYEE_SERVICE.complete_profile_by_email(data, session)


@router.delete("/employee/{employee_id}")
async def delete_employee(
    employee_id: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("employees:write")),
):
    return await EMPLOYEE_SERVICE.delete(employee_id, session)


@router.delete("/employee/email/{email}")
async def delete_employee_by_email(
    email: str,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("employees:write")),
):
    return await EMPLOYEE_SERVICE.delete_by_email(email, session)


@router.delete("/employee/documentid/{documentid}")
async def delete_employee_by_documentid(
    documentid: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("employees:write")),
):
    return await EMPLOYEE_SERVICE.delete_by_documentid(documentid, session)


@router.get("/employee", response_model=Page[EmployeeRead])
async def list_employees(
    query=QueryBuilder(Employee),
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("employees:all:read")),
):
    return await apaginate(session, query)
