from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.dataset import DatasetMetadata

router = APIRouter(prefix="/datasets/upload", tags=["upload"])

@router.post("", response_model=DatasetMetadata)
async def upload_dataset(file: UploadFile = File(...)):
    raise HTTPException(status_code=501, detail="Upload endpoint not implemented yet. Will be implemented in Phase 3.")
