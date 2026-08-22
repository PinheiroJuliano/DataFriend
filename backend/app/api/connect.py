import os
import uuid
import json
import httpx
import pandas as pd
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.dataset import DatasetMetadata
from app.data.loader import load_dataset
from app.data.registry import register_dataset
from app.data.duckdb import DuckDBManager
from app.config import settings

router = APIRouter(prefix="/datasets/connect", tags=["connect"])


class ConnectURLRequest(BaseModel):
    url: str
    name: Optional[str] = None
    headers: Optional[dict] = None


class ConnectDBRequest(BaseModel):
    connection_string: str
    query: str
    name: Optional[str] = None


@router.post("/url", response_model=DatasetMetadata)
async def connect_url(request: ConnectURLRequest):
    """
    Fetches JSON data from a REST API URL and loads it into DuckDB.
    The API must return a JSON array of objects or an object with a key containing an array.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = request.headers or {}
            response = await client.get(request.url, headers=headers)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao acessar a API: HTTP {e.response.status_code}",
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro de conexão: {str(e)}",
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="A resposta não é JSON válido.",
        )

    # Try to extract array from common wrapper keys
    if isinstance(data, dict):
        for key in ["data", "results", "items", "records", "rows"]:
            if key in data and isinstance(data[key], list):
                data = data[key]
                break
        else:
            raise HTTPException(
                status_code=400,
                detail="O JSON retornado não contém um array de dados. "
                       "Envie um array [{...}, ...] ou um objeto com chave 'data', 'results', etc.",
            )

    if not isinstance(data, list) or len(data) == 0:
        raise HTTPException(
            status_code=400,
            detail="O JSON deve conter um array não vazio de objetos.",
        )

    # Convert to DataFrame
    try:
        df = pd.DataFrame(data)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Não foi possível converter os dados: {str(e)}",
        )

    # Save as CSV temporarily and load into DuckDB
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
            detail=f"Erro ao processar dados da API: {str(exc)}",
        )

    name = request.name or request.url.split("/")[-1] or "api_data"
    register_dataset(dataset_id, name)

    return DatasetMetadata(
        dataset_id=metadata["dataset_id"],
        filename=name,
        rows_count=metadata["rows_count"],
        columns_count=metadata["columns_count"],
        schema_info=metadata["schema_info"],
    )


@router.post("/db", response_model=DatasetMetadata)
async def connect_database(request: ConnectDBRequest):
    """
    Connects to a PostgreSQL database using a connection string,
    runs a query, and loads the results into DuckDB.
    """
    try:
        import psycopg2
        import sqlalchemy
        from sqlalchemy import create_engine
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Driver de banco de dados não instalado. Instale: pip install psycopg2-binary sqlalchemy",
        )

    try:
        engine = create_engine(request.connection_string)
        df = pd.read_sql(request.query, engine)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao consultar o banco: {str(e)}",
        )

    if df.empty:
        raise HTTPException(
            status_code=400,
            detail="A consulta não retornou dados.",
        )

    # Save and load
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
            detail=f"Erro ao processar dados do banco: {str(exc)}",
        )

    name = request.name or "database_data"
    register_dataset(dataset_id, name)

    return DatasetMetadata(
        dataset_id=metadata["dataset_id"],
        filename=name,
        rows_count=metadata["rows_count"],
        columns_count=metadata["columns_count"],
        schema_info=metadata["schema_info"],
    )
