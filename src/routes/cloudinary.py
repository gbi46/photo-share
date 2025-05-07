from fastapi import APIRouter, UploadFile, File, Form
from src.database.models import User
from src.core.dependencies import require_role
from src.services.cloudinary import UploadFileService

router = APIRouter(prefix='/cloudinary', tags=['cloudinary'])

@router.post("/upload-image")
async def cloudinary_upload_image(
    file: UploadFile = File(...),
    width: str = Form(...),
    height: str = Form(...),
    crop: str = Form(...),
    effect: str = Form(...),
    user: User = require_role('user'),
):
    image_url = await UploadFileService.upload_file(
        file=file, 
        width=width,
        height=height,
        crop=crop,
        effect=effect
    )

    return {"image_url": image_url}
