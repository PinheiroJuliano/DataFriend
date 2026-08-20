import os
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.models.dataset import DatasetMetadata
from app.data.loader import load_dataset
from app.data.registry import register_dataset
from app.config import settings

router = APIRouter(prefix="/datasets/upload", tags=["upload"])

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}

@router.post("", response_model=DatasetMetadata)
async def upload_dataset(file: UploadFile = File(...)):
    original_filename = file.filename or ""
    ext = os.path.splitext(original_filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato não suportado: '{ext or 'sem extensão'}'. Envie um arquivo CSV ou XLSX.",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="O arquivo enviado está vazio.")

    upload_dir = settings.upload_dir
    os.makedirs(upload_dir, exist_ok=True)

    dataset_id = uuid.uuid4().hex
    stored_filename = f"{dataset_id}{ext}"
    file_path = os.path.join(upload_dir, stored_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(content)

    try:
        metadata = load_dataset(file_path, dataset_id)
    except Exception as exc:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail=f"Não foi possível processar o arquivo: {str(exc)}",
        )

    register_dataset(dataset_id, original_filename)

    return DatasetMetadata(
        dataset_id=metadata["dataset_id"],
        filename=original_filename,
        rows_count=metadata["rows_count"],
        columns_count=metadata["columns_count"],
        schema_info=metadata["schema_info"],
    )
