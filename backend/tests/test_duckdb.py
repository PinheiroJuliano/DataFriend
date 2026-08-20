import os
import sys
import pytest
import pandas as pd

# Add app folder to search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.data.duckdb import DuckDBManager
from app.data.loader import load_dataset

def test_duckdb_csv_loading_and_querying(tmp_path):
    # Setup temporary duckdb database
    db_path = str(tmp_path / "test.duckdb")
    db_manager = DuckDBManager(db_path=db_path)
    
    # We will use the existing sample_sales.csv
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_sales.csv"))
    assert os.path.exists(csv_path), f"CSV not found at {csv_path}"
    
    dataset_id = "test_sales"
    
    # Load dataset
    metadata = load_dataset(csv_path, dataset_id, db_manager=db_manager)
    
    # Verify metadata
    assert metadata["dataset_id"] == dataset_id
    assert metadata["filename"] == "sample_sales.csv"
    assert metadata["rows_count"] == 5
    assert metadata["columns_count"] == 7
    assert "produto" in metadata["schema_info"]
    assert "valor" in metadata["schema_info"]
    
    # Test SELECT query on the virtual view 'data'
    columns, rows = db_manager.execute_query("SELECT SUM(valor) FROM data", dataset_id=dataset_id)
    assert columns == ["sum(valor)"]
    assert len(rows) == 1
    assert rows[0][0] == 22500.0  # 8000 + 1500 + 4000 + 6000 + 3000 = 22500
    
    # Test schema retrieval via manager
    schema = db_manager.get_dataset_schema(dataset_id)
    assert schema["produto"] in ["VARCHAR", "TEXT"]
    assert schema["quantidade"] in ["BIGINT", "INTEGER"]
    
    # Test SELECT filtering
    cols, data_rows = db_manager.execute_query("SELECT produto FROM data WHERE estado = 'SP' ORDER BY id", dataset_id=dataset_id)
    assert cols == ["produto"]
    assert data_rows == [["Notebook"], ["Monitor"]]

def test_duckdb_xlsx_loading_and_querying(tmp_path):
    # Setup temporary duckdb database
    db_path = str(tmp_path / "test_xlsx.duckdb")
    db_manager = DuckDBManager(db_path=db_path)
    
    # Create a temporary excel file
    excel_path = str(tmp_path / "test_data.xlsx")
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "score": [95.5, 88.0, 72.3]
    })
    df.to_excel(excel_path, index=False)
    
    dataset_id = "test_excel_id"
    
    # Load dataset
    metadata = load_dataset(excel_path, dataset_id, db_manager=db_manager)
    
    # Verify metadata
    assert metadata["dataset_id"] == dataset_id
    assert metadata["filename"] == "test_data.xlsx"
    assert metadata["rows_count"] == 3
    assert metadata["columns_count"] == 3
    assert "name" in metadata["schema_info"]
    assert "score" in metadata["schema_info"]
    
    # Test SELECT query on 'data' view
    columns, rows = db_manager.execute_query("SELECT AVG(score) FROM data", dataset_id=dataset_id)
    assert columns == ["avg(score)"]
    assert len(rows) == 1
    assert pytest.approx(rows[0][0], 0.01) == 85.26
    
    # Test querying with specific filtering
    cols, data_rows = db_manager.execute_query("SELECT name FROM data WHERE score > 80 ORDER BY id", dataset_id=dataset_id)
    assert data_rows == [["Alice"], ["Bob"]]

def test_duckdb_errors(tmp_path):
    db_path = str(tmp_path / "test_errors.duckdb")
    db_manager = DuckDBManager(db_path=db_path)
    
    # 1. Non-existent dataset_id query error
    with pytest.raises(ValueError, match="Dataset table 'dataset_non_existent' does not exist"):
        db_manager.execute_query("SELECT * FROM data", dataset_id="non-existent")
        
    # 2. Non-existent file loading error
    with pytest.raises(FileNotFoundError):
        load_dataset(str(tmp_path / "non_existent_file.csv"), "some_id", db_manager=db_manager)
        
    # 3. Unsupported file extension error
    invalid_file = tmp_path / "invalid_file.txt"
    invalid_file.write_text("dummy content")
    with pytest.raises(ValueError, match="Unsupported file format"):
        load_dataset(str(invalid_file), "some_id", db_manager=db_manager)
        
    # 4. Invalid SQL syntax execution error
    # We load a valid file first
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_sales.csv"))
    load_dataset(csv_path, "valid_id", db_manager=db_manager)
    # Executing invalid SQL should raise an exception from DuckDB
    import duckdb
    with pytest.raises((duckdb.ParserException, duckdb.CatalogException)):
        db_manager.execute_query("SELECT * FROM non_existent_table", dataset_id="valid_id")
