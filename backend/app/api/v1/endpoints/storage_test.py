"""Storage testing endpoint"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from app.services.storage import get_storage
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/storage/test-upload")
async def test_upload(file: UploadFile = File(...)):
    """Test file upload to storage"""
    try:
        storage = await get_storage()
        
        # Read file data
        file_data = await file.read()
        
        # Generate storage key
        key = f"test/{file.filename}"
        
        # Upload to storage
        url = await storage.upload(
            key=key,
            data=file_data,
            content_type=file.content_type or "application/octet-stream"
        )
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "provider": storage.config.provider,
            "url": url,
            "key": key,
            "size": len(file_data),
            "content_type": file.content_type
        }
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/storage/test-download/{key:path}")
async def test_download(key: str):
    """Test file download from storage"""
    try:
        storage = await get_storage()
        
        # Check if file exists
        if not await storage.exists(key):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Download file
        file_data = await storage.download(key)
        
        return Response(
            content=file_data,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={key.split('/')[-1]}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/storage/test-presigned/{key:path}")
async def test_presigned_url(key: str, expiration: int = 3600):
    """Test presigned URL generation"""
    try:
        storage = await get_storage()
        
        # Check if file exists
        if not await storage.exists(key):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Generate presigned URL
        url = await storage.get_presigned_url(key, expiration)
        
        return {
            "success": True,
            "provider": storage.config.provider,
            "presigned_url": url,
            "expires_in": expiration,
            "key": key
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Presigned URL failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/storage/test-delete/{key:path}")
async def test_delete(key: str):
    """Test file deletion"""
    try:
        storage = await get_storage()
        
        # Delete file
        success = await storage.delete(key)
        
        return {
            "success": success,
            "provider": storage.config.provider,
            "message": "File deleted successfully" if success else "Delete failed",
            "key": key
        }
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
