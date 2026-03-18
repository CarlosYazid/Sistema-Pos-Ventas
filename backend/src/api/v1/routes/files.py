from botocore.client import BaseClient
from fastapi import APIRouter, Depends

from core.storage import get_e2_client
from core.auth import require_scope
from services import FileService

router = APIRouter(prefix="/files", tags=["Files"])

FILESERVICE = FileService()


@router.get("/{key:path}")
async def get_file(
    key: str,
    storage_client: BaseClient = Depends(get_e2_client),
    
):
    """
    Retrieve a file by path.
    """
    return await FILESERVICE.get_file(key, storage_client)
