from pydantic import SecretStr

from core.settings import SETTINGS
from tasks.generate_invoice import generate_invoice_task


class DummyTemplate:
    def render(self, **kwargs):
        return "<html><body>ok</body></html>"


class DummyEnv:
    def get_template(self, name: str):
        return DummyTemplate()


class DummyHTML:
    def __init__(self, string: str, base_url: str | None = None):
        self.string = string
        self.base_url = base_url

    def write_pdf(self):
        return b"%PDF-1.4\n%Dummy"


def test_generate_invoice_task_dry_run(monkeypatch):
    SETTINGS.secret_key = SecretStr("test-secret")
    SETTINGS.jinja_env = DummyEnv()

    payload = {
        "order_id": 1,
        "order_status": "Pendiente",
        "invoice": {
            "number": 1,
            "date": "2026-03-13T00:00:00",
            "client": {"name": "Test", "email": "test@example.com", "phone": ""},
            "subtotal": 10.0,
            "tax_rate": 0.0,
            "tax_amount": 0.0,
            "total": 10.0,
        },
        "items": [
            {"type": "product", "name": "Item", "quantity": 1, "unit_price": 10.0, "total": 10.0}
        ],
        "verification_token": "token.sig",
        "pdf_key": "invoices/1-token.pdf",
        "client_email": "test@example.com",
        "client_name": "Test",
    }

    monkeypatch.setattr(
        "tasks.generate_invoice.generate_qr_data_url",
        lambda url: "data:image/png;base64,xxx",
    )
    monkeypatch.setattr("tasks.generate_invoice.upload_invoice_pdf", lambda pdf, key: None)
    monkeypatch.setattr(
        "tasks.generate_invoice.update_order_pdf_key",
        lambda order_id, pdf_key, verification_token=None: None,
    )
    monkeypatch.setattr("tasks.generate_invoice.send_invoice_email", lambda *args, **kwargs: None)
    monkeypatch.setattr("tasks.generate_invoice.HTML", DummyHTML)

    result = generate_invoice_task.run(order_id=1, payload=payload, attach_pdf=False)

    assert result["pdf_key"] == payload["pdf_key"]
    assert result["verification_token"] == payload["verification_token"]
