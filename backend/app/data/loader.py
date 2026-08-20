import os
import pandas as pd
from app.data.duckdb import DuckDBManager

def load_dataset(file_path: str, dataset_id: str, db_manager: DuckDBManager = None) -> dict:
    """
    Loads a CSV or XLSX file into DuckDB under the table dataset_{dataset_id}.
    Returns metadata dict with keys: dataset_id, filename, rows_count, columns_count, schema_info.
    """
    if db_manager is None:
        db_manager = DuckDBManager()
        
    sanitized_id = dataset_id.replace("-", "_")
    table_name = f"dataset_{sanitized_id}"
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    filename = os.path.basename(file_path)
    _, ext = os.path.splitext(filename.lower())
    
    conn = db_manager.get_connection()
    try:
        if ext == ".csv":
            # Load CSV natively via DuckDB
            # We use read_csv_auto which is highly robust.
            # Convert backslashes to forward slashes for DuckDB compatibility
            normalized_path = file_path.replace("\\", "/")
            conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_csv_auto('{normalized_path}')")
        elif ext in [".xlsx", ".xls"]:
            # Load XLSX using pandas
            df = pd.read_excel(file_path)
            # Ensure all column names are strings
            df.columns = [str(col) for col in df.columns]
            
            # Insert/Create table in DuckDB using the pandas DataFrame
            conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")
        else:
            raise ValueError(f"Unsupported file format: {ext}")
            
        # Retrieve the metadata
        metadata = db_manager.get_dataset_metadata(dataset_id)
        
        return {
            "dataset_id": dataset_id,
            "filename": filename,
            "rows_count": metadata["rows_count"],
            "columns_count": metadata["columns_count"],
            "schema_info": metadata["schema"]
        }
    finally:
        conn.close()
