from src.conf.config import settings
from fastapi import UploadFile, HTTPException

import cloudinary
import cloudinary.uploader

class UploadFileService:
    @staticmethod
    def configure_cloudinary():
        cloudinary.config(
            cloud_name=settings.CLD_NAME,
            api_key=settings.CLD_API_KEY,
            api_secret=settings.CLD_API_SECRET
        )

    @staticmethod
    async def upload_file(
        file: UploadFile,
        width: int,
        height: int,
        crop: str,
        effect: str,
    ) -> str:
        UploadFileService.configure_cloudinary()

        try:
            result = cloudinary.uploader.upload(file.file)
            public_id = result.get("public_id")

            transformation = {
                "width": width,
                "height": height,
                "crop": crop,
                "effect": effect
            }

            url_link = cloudinary.CloudinaryImage(public_id).build_url(
                transformation=transformation,
                version=result.get("version")
            )
            return url_link
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Upload with filters failed: {str(e)}")