from fastapi import APIRouter, HTTPException

from app.models.dataset import DatasetMetadata
from app.data.duckdb import DuckDBManager
from app.data.registry import get_filename

router = APIRouter(prefix="/datasets", tags=["datasets"])

@router.get("/{dataset_id}", response_model=DatasetMetadata)
async def get_dataset_metadata(dataset_id: str):
    filename = get_filename(dataset_id)
    if filename is None:
        raise HTTPException(status_code=404, detail="Dataset não encontrado.")

    db_manager = DuckDBManager()
    try:
        meta = db_manager.get_dataset_metadata(dataset_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return DatasetMetadata(
        dataset_id=dataset_id,
        filename=filename,
        rows_count=meta["rows_count"],
        columns_count=meta["columns_count"],
        schema_info=meta["schema"],
    )
