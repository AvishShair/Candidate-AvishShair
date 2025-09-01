from fastapi import APIRouter, UploadFile, File, HTTPException, status, Form
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import os
import uuid
from pathlib import Path
import asyncio
import hashlib
import json
import requests
import logging

from config import settings
from video_processor import VideoProcessor
router = APIRouter()
UPLOAD_DIR = Path(settings.UPLOAD_FOLDER)
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

def get_video_hash(file_path: str) -> str:
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

@router.post("/process-video")
async def upload_video(
    file: UploadFile = File(...),
    guide_id: Optional[int] = Form(None),
    callback_url: Optional[str] = Form(None)
) -> Dict[str, Any]:
    if not any(file.filename.lower().endswith(ext) for ext in settings.ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    file_ext = Path(file.filename).suffix
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / filename
    
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process video directly without caching
        video_hash = hashlib.sha256(content).hexdigest()
        
        # Create processor instance and process video
        processor = VideoProcessor()
        # Use provided guide_id or generate a random one
        actual_guide_id = guide_id if guide_id is not None else hash(video_hash) % 10000
        
        # Since process_video is not async, we need to run it in a thread pool
        result = await asyncio.get_event_loop().run_in_executor(
            None, 
            processor.process_video, 
            str(file_path), 
            actual_guide_id
        )
        
        
        result["cached"] = False
        
        # Send callback if URL is provided
        if callback_url:
            await send_callback(callback_url, result, actual_guide_id)
        
        return result
        
    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        if file_path.exists() and not settings.DEBUG:
            try:
                file_path.unlink()
            except:
                pass

async def send_callback(callback_url: str, result: Dict[str, Any], guide_id: int):
    """Send processing result to callback URL"""
    logger = logging.getLogger(__name__)
    
    try:
        callback_payload = {
            "guide_id": guide_id,
            "status": "completed",
            "result": result,
            "timestamp": result.get("timestamp", None)
        }
        
        # Send callback in background to avoid blocking response
        response = requests.post(
            callback_url,
            json=callback_payload,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            logger.info(f"Callback sent successfully to {callback_url} for guide_id {guide_id}")
        else:
            logger.warning(f"Callback failed with status {response.status_code} for {callback_url}")
            
    except Exception as e:
        logger.error(f"Failed to send callback to {callback_url}: {str(e)}")
