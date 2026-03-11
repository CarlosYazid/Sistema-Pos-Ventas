from typing import Any, Dict, Optional

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr
from supertokens_python.ingredients.emaildelivery.types import EmailDeliveryInterface
from supertokens_python.recipe.emailpassword.types import PasswordResetEmailTemplateVars
from supertokens_python.recipe.emailverification.types import VerificationEmailTemplateVars

from core import SETTINGS


class EmailSchema(BaseModel):
    body: Optional[str] = None
    subject: str
    recipients: list[EmailStr]
    subtype: Any
    template_body: Optional[dict[str, Any]] = None


class EmailService:
    def __init__(self, email_conf: ConnectionConfig):
        self.fm = FastMail(email_conf)

    async def send_email(self, email_data: EmailSchema, template_name: str | None = None) -> None:
        if template_name is not None:
            await self.fm.send_message(
                MessageSchema(**email_data.model_dump()), template_name=template_name
            )
        else:
            await self.fm.send_message(MessageSchema(**email_data.model_dump()))


class SuperTokensEmailVerificationService(EmailDeliveryInterface[VerificationEmailTemplateVars]):
    def __init__(self, email_service: EmailService):
        self.email_service = email_service

    async def send_email(
        self,
        template_vars: VerificationEmailTemplateVars,
        user_context: Dict,
    ) -> None:
        email_data = EmailSchema(
            subject=f"{SETTINGS.app_name} - Verifica tu correo",
            recipients=[template_vars.user.email],
            subtype=MessageType.html,
            template_body={
                "app_name": SETTINGS.app_name,
                "email": template_vars.user.email,
                "verify_link": template_vars.email_verify_link,
            },
        )

        await self.email_service.send_email(email_data, template_name="email_verification.html")


class SuperTokensPasswordResetService(EmailDeliveryInterface[PasswordResetEmailTemplateVars]):
    def __init__(self, email_service: EmailService):
        self.email_service = email_service

    async def send_email(
        self,
        template_vars: PasswordResetEmailTemplateVars,
        user_context: Dict,
    ) -> None:
        email_data = EmailSchema(
            subject=f"{SETTINGS.app_name} - Restablece tu contrasena",
            recipients=[template_vars.user.email],
            subtype=MessageType.html,
            template_body={
                "app_name": SETTINGS.app_name,
                "email": template_vars.user.email,
                "reset_link": template_vars.password_reset_link,
            },
        )

        await self.email_service.send_email(email_data, template_name="reset_email.html")
