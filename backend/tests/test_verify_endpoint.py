import asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from api.v1.routes.order import orders_router
from core import get_e2_client
from core.settings import SETTINGS
from db import get_session
from models import Client, Employee, Order, OrderStatus
from utils.signer import sign_token


class FakeStorageClient:
    async def get_object(self, Bucket: str, Key: str):
        return {"Body": iter([b"pdf-bytes"]), "ContentType": "application/pdf"}


async def override_get_e2_client():
    yield FakeStorageClient()


def build_test_app():
    app = FastAPI()
    app.include_router(orders_router, prefix="/v1")
    return app


def setup_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def init():
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        async with async_session() as session:
            client = Client(email="client@example.com")
            employee = Employee(email="emp@example.com", user_id="user-1")
            session.add(client)
            session.add(employee)
            await session.commit()
            await session.refresh(client)
            await session.refresh(employee)

            signed = sign_token("token123")
            order = Order(
                client_id=client.id,
                employee_id=employee.id,
                total_price=10.0,
                status=OrderStatus.PENDING,
                verification_token=signed,
                pdf_key="invoices/test.pdf",
            )
            session.add(order)
            await session.commit()

        return signed, async_session

    signed_token, session_factory = asyncio.run(init())
    return engine, session_factory, signed_token


def test_verify_invoice_endpoint():
    SETTINGS.secret_key = SecretStr("test-secret")

    engine, session_factory, signed_token = setup_db()

    async def override_get_session():
        async with session_factory() as session:
            yield session

    app = build_test_app()
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_e2_client] = override_get_e2_client

    client = TestClient(app)
    response = client.get(f"/v1/orders/invoices/{signed_token}")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")

    asyncio.run(engine.dispose())


def test_verify_invoice_invalid_token():
    SETTINGS.secret_key = SecretStr("test-secret")

    engine, session_factory, signed_token = setup_db()

    async def override_get_session():
        async with session_factory() as session:
            yield session

    app = build_test_app()
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_e2_client] = override_get_e2_client

    client = TestClient(app)
    response = client.get(f"/v1/orders/invoices/{signed_token}x")

    assert response.status_code == 403

    asyncio.run(engine.dispose())
