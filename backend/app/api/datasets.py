from fastapi import APIRouter, HTTPException
from app.models.dataset import DatasetMetadata

router = APIRouter(prefix="/datasets", tags=["datasets"])

@router.get("/{dataset_id}", response_model=DatasetMetadata)
async def get_dataset_metadata(dataset_id: str):
    raise HTTPException(status_code=501, detail="Datasets metadata endpoint not implemented yet. Will be implemented in Phase 3.")
