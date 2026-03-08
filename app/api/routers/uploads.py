from fastapi import APIRouter
from app.dependencies import CurrentUser
from app.schemas.upload import PresignedRequest, PresignedURLItem, ConfirmUploadRequest, ConfirmedPhoto
from app.services.storage import StorageService
from app.core.exceptions import ValidationError

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/presigned", response_model=list[PresignedURLItem])
async def get_presigned_urls(body: PresignedRequest, current_user: CurrentUser):
    svc = StorageService()
    return svc.generate_presigned_urls(body.count, item_id=body.item_id)


@router.post("/confirm", response_model=list[ConfirmedPhoto])
async def confirm_uploads(body: ConfirmUploadRequest, current_user: CurrentUser):
    svc = StorageService()
    try:
        return svc.confirm_uploads(body.keys)
    except ValueError as e:
        raise ValidationError(str(e))
