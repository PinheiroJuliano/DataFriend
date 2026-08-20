import os
import sys

# Point storage to temp locations BEFORE importing the app (config is read at import)
TMP_ROOT = os.path.join(os.path.dirname(__file__), "tmp_test_upload")
os.makedirs(TMP_ROOT, exist_ok=True)
os.environ["DUCKDB_PATH"] = os.path.join(TMP_ROOT, "test.duckdb")
os.environ["UPLOAD_DIR"] = os.path.join(TMP_ROOT, "uploads")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

SAMPLE_CSV = (
    "id,data,produto,categoria,estado,quantidade,valor\n"
    "1,2025-01-10,Notebook,Eletronicos,SP,2,8000\n"
    "2,2025-01-12,Mouse,Perifericos,MG,10,1500\n"
)

def test_upload_csv_and_get_metadata():
    response = client.post(
        "/api/datasets/upload",
        files={"file": ("vendas.csv", SAMPLE_CSV.encode("utf-8"), "text/csv")},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["filename"] == "vendas.csv"
    assert body["rows_count"] == 2
    assert body["columns_count"] == 7
    assert "produto" in body["schema_info"]
    dataset_id = body["dataset_id"]
    assert dataset_id

    # The same dataset must be retrievable via GET
    get_resp = client.get(f"/api/datasets/{dataset_id}")
    assert get_resp.status_code == 200, get_resp.text
    get_body = get_resp.json()
    assert get_body["dataset_id"] == dataset_id
    assert get_body["filename"] == "vendas.csv"
    assert get_body["rows_count"] == 2
    assert get_body["schema_info"] == body["schema_info"]

def test_upload_rejects_unsupported_format():
    response = client.post(
        "/api/datasets/upload",
        files={"file": ("doc.txt", b"not a csv", "text/plain")},
    )
    assert response.status_code == 400
    assert "não suportado" in response.json()["detail"] or "suportado" in response.json()["detail"]

def test_upload_rejects_empty_file():
    response = client.post(
        "/api/datasets/upload",
        files={"file": ("empty.csv", b"", "text/csv")},
    )
    assert response.status_code == 400
    assert "vazio" in response.json()["detail"]

def test_get_missing_dataset_returns_404():
    response = client.get("/api/datasets/does-not-exist")
    assert response.status_code == 404

def test_upload_xlsx_and_get_metadata(tmp_path):
    xlsx_path = os.path.join(tmp_path, "planilha.xlsx")
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "nome": ["A", "B", "C"],
        "valor": [10.0, 20.0, 30.0],
    })
    df.to_excel(xlsx_path, index=False)

    with open(xlsx_path, "rb") as f:
        content = f.read()

    response = client.post(
        "/api/datasets/upload",
        files={"file": ("planilha.xlsx", content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["filename"] == "planilha.xlsx"
    assert body["rows_count"] == 3
    assert body["columns_count" ] == 3

    get_resp = client.get(f"/api/datasets/{body['dataset_id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["filename"] == "planilha.xlsx"
