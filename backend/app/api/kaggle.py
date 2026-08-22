import os
import uuid
import pandas as pd
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.dataset import DatasetMetadata
from app.data.loader import load_dataset
from app.data.registry import register_dataset
from app.config import settings

router = APIRouter(prefix="/datasets/kaggle", tags=["kaggle"])


class KaggleConnectRequest(BaseModel):
    dataset: str
    file_path: str
    name: Optional[str] = None


@router.post("", response_model=DatasetMetadata)
async def connect_kaggle(request: KaggleConnectRequest):
    """
    Loads a dataset from Kaggle using kagglehub.
    Dataset format: "owner/dataset-name" (e.g. "vinothkannaece/sales-dataset")
    """
    username = settings.kaggle_username
    key = settings.kaggle_key

    if not username or not key:
        raise HTTPException(
            status_code=500,
            detail="Credenciais do Kaggle não configuradas. Defina KAGGLE_USERNAME e KAGGLE_KEY no .env",
        )

    # Set Kaggle environment variables
    os.environ["KAGGLE_USERNAME"] = username
    os.environ["KAGGLE_KEY"] = key

    try:
        import kagglehub
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="kagglehub não instalado. Instale: pip install kagglehub[pandas-datasets]",
        )

    try:
        # Download the dataset - returns a directory
        download_path = kagglehub.dataset_download(
            request.dataset,
        )

        # Find the requested file in the download directory
        if os.path.isfile(download_path):
            file_path_local = download_path
        else:
            file_path_local = os.path.join(download_path, request.file_path)
            if not os.path.exists(file_path_local):
                # List available files and show error
                available = [f for f in os.listdir(download_path) if os.path.isfile(os.path.join(download_path, f))]
                raise HTTPException(
                    status_code=400,
                    detail=f"Arquivo '{request.file_path}' não encontrado. Disponíveis: {', '.join(available)}",
                )

        # Try multiple encodings
        encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1", "utf-16"]
        df = None
        for enc in encodings:
            try:
                df = pd.read_csv(file_path_local, encoding=enc)
                break
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue

        if df is None:
            raise HTTPException(
                status_code=400,
                detail="Não foi possível ler o arquivo com nenhuma codificação suportada.",
            )

        if df is None or df.empty:
            raise HTTPException(
                status_code=400,
                detail="O dataset do Kaggle está vazio ou não foi encontrado.",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao carregar dataset do Kaggle: {str(e)}",
        )

    # Ensure column names are strings
    df.columns = [str(col) for col in df.columns]

    # Save as CSV and load into DuckDB
    dataset_id = uuid.uuid4().hex
    temp_path = os.path.join(settings.upload_dir, f"{dataset_id}.csv")
    os.makedirs(settings.upload_dir, exist_ok=True)

    try:
        df.to_csv(temp_path, index=False)
        metadata = load_dataset(temp_path, dataset_id)
    except Exception as exc:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao processar dataset: {str(exc)}",
        )

    name = request.name or request.dataset.split("/")[-1]
    register_dataset(dataset_id, name)

    return DatasetMetadata(
        dataset_id=metadata["dataset_id"],
        filename=name,
        rows_count=metadata["rows_count"],
        columns_count=metadata["columns_count"],
        schema_info=metadata["schema_info"],
    )
