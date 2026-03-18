import base64
import io
import hashlib
import hmac
import uuid

import qrcode
from botocore.client import BaseClient
from PIL import Image

from core.settings import SETTINGS

class OrderUtils:
    
    def create_token(self) -> str:
        """Crea un token base (UUID) para la verificacion."""
        return uuid.uuid4().hex
    
    def sign_token(self, token: str) -> str:
        """Firma un token con HMAC-SHA256 y retorna token.firma."""
        signature = hmac.new(
            SETTINGS.secret_key.get_secret_value().encode("utf-8"), 
            token.encode("utf-8"), 
            hashlib.sha256).digest()
        return f"{token}.{base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")}"
    
    def verify_signature(self, signed_token: str) -> str | None:
        """Valida la firma y retorna el token base si es valido."""
        
        try:
            token, signature = signed_token.rsplit(".", 1)
        except ValueError:
            return None
        
        expected = self.sign_token(token).rsplit(".", 1)[1]
        
        if not hmac.compare_digest(signature, expected):
            return None
        
        return token
    
    def build_verify_url(self, verification_token: str) -> str:
        return f"{SETTINGS.api_domain}/{SETTINGS.version}/order/verify/{verification_token}"
    
    def build_invoice_pdf_key(self, order_id: int, raw_token: str) -> str:
        return f"{SETTINGS.invoice_folder}/{order_id}-{raw_token}.pdf"
    
    def generate_qr_data_url(self, url: str) -> str:
        """Genera un QR PNG en memoria y lo convierte a data URL."""
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=5, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        image = qr.make_image(fill_color="black", back_color="white")
        image = image.resize((60, 60), Image.Resampling.LANCZOS)
        
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"

    async def upload_invoice(self, pdf_bytes: bytes, key: str, storage_client: BaseClient) -> None:
        """Sube el PDF al storage usando aioboto3."""
        
        async for client in storage_client:
            await client.put_object(
                Bucket=SETTINGS.bucket_name, Key=key,
                Body=pdf_bytes, ContentType="application/pdf")