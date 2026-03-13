from enum import Enum
from pathlib import Path
from typing import Optional

from fastapi_mail import ConnectionConfig
from jinja2 import Environment as JinjaEnvironment
from jinja2 import FileSystemLoader, select_autoescape
from pydantic import EmailStr, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class Environment(str, Enum):
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"
    STAGING = "stag"


class Settings(BaseSettings):
    BACKEND_DIR: Path = BACKEND_DIR

    model_config = SettingsConfigDict(
        env_file=(str(BACKEND_DIR / ".env"), str(BACKEND_DIR.parent / ".env")),
        env_file_encoding="utf-8",
        extra="allow",
    )

    # General
    app_name: str = "SalesApp"
    description: str = "Sales system API REST"
    version: str = "v1"
    environment: Environment = Environment.DEVELOPMENT
    host: str = '127.0.0.1'
    port: int = 8080

    # Database
    db_url_sync: str
    db_url_async: str

    # Storage
    storage_endpoint_url: str
    storage_access_key: SecretStr
    storage_secret_key: SecretStr
    storage_region: str
    bucket_name: str
    image_folder: str
    invoice_folder: str

    # Email
    smtp_user: str
    smtp_pass: SecretStr
    smtp_server: str
    smtp_port: int
    smtp_starttls: bool = True
    smtp_ssl: bool = False
    smtp_use_credentials: bool = True
    email_conf: Optional[ConnectionConfig] = None

    # Templates
    templates_folder: str = Field(default_factory=lambda: str(BACKEND_DIR / "src/templates"))
    jinja_env: Optional[JinjaEnvironment] = None

    # Company
    company_name: str
    company_email: EmailStr
    company_phone: str
    company_address: str
    website_domain: str = "http://localhost:3000"
    footer_message: str

    # Auth
    supertokens_host: str
    supertokens_port: int
    supertokens_url: Optional[str] = Field(default=None)
    google_client_id: str
    google_client_secret: SecretStr
    dashboard_api_key: Optional[str] = None
    tenant_id: str = Field(default="public")
    default_role: str = Field(default="employee")

    # Logfire
    logfire_token: SecretStr

    # CORS
    allowed_origins: list[str] = Field(default_factory=list)
    allow_credentials: bool = True
    allow_methods: list[str] = Field(default_factory=list)

    def model_post_init(self, __context) -> None:
        if self.environment != Environment.PRODUCTION:
            self.allowed_origins.append("*")
            self.allow_methods.append("*")
            self.smtp_server = "mailhog"
            self.smtp_port = 1025
            self.smtp_starttls = False
            self.smtp_ssl = False
            self.smtp_use_credentials = False

        else:
            self.allowed_origins.append(self.website_domain)

            self.allow_methods.extend(["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"])

        self.supertokens_url = self.supertokens_host + ":" + str(self.supertokens_port)

        self.email_conf = ConnectionConfig(
            MAIL_USERNAME=self.smtp_user,
            MAIL_PASSWORD=self.smtp_pass.get_secret_value().replace(" ", "").strip(),
            MAIL_FROM=self.smtp_user,
            MAIL_PORT=self.smtp_port,
            MAIL_SERVER=self.smtp_server,
            MAIL_STARTTLS=self.smtp_starttls,
            MAIL_SSL_TLS=self.smtp_ssl,
            USE_CREDENTIALS=self.smtp_use_credentials,
            VALIDATE_CERTS=True,
            TEMPLATE_FOLDER=self.templates_folder,
        )

        self.jinja_env = JinjaEnvironment(
            loader=FileSystemLoader(self.templates_folder),
            autoescape=select_autoescape(["html", "xml"]),
        )


SETTINGS = Settings()
