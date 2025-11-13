import cloudinary
import cloudinary.uploader
import os

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_image_to_cloudinary(file_storage):
    """Sube un archivo FileStorage (imagen) a Cloudinary"""
    result = cloudinary.uploader.upload(file_storage, folder="tableros")
    return result.get("secure_url")