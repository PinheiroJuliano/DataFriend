import os
import duckdb
from typing import Dict, List, Any, Tuple

from app.config import settings

class DuckDBManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = settings.duckdb_path
        
        # Ensure directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            
        self.db_path = db_path

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """
        Returns a connection to the DuckDB file.
        """
        return duckdb.connect(self.db_path)

    def execute_query(self, query: str, dataset_id: str = None) -> Tuple[List[str], List[List[Any]]]:
        """
        Executes a query and returns columns and rows.
        If dataset_id is provided, it sets up a temporary view 'data' pointing to dataset_{dataset_id}
        before executing the query.
        """
        conn = self.get_connection()
        try:
            if dataset_id:
                sanitized_id = dataset_id.replace("-", "_")
                # Check if table exists
                table_exists = conn.execute(
                    f"SELECT count(*) FROM information_schema.tables WHERE table_name = 'dataset_{sanitized_id}'"
                ).fetchone()[0] > 0
                
                if not table_exists:
                    raise ValueError(f"Dataset table 'dataset_{sanitized_id}' does not exist.")
                    
                conn.execute(f"CREATE OR REPLACE TEMP VIEW data AS SELECT * FROM dataset_{sanitized_id}")
            
            # Execute the actual query
            result = conn.execute(query)
            columns = [desc[0] for desc in result.description]
            rows = result.fetchall()
            
            # Convert rows to standard python lists
            return columns, [list(row) for row in rows]
        finally:
            conn.close()

    def get_dataset_schema(self, dataset_id: str) -> Dict[str, str]:
        """
        Returns the schema (column name -> type) for the specified dataset.
        """
        conn = self.get_connection()
        try:
            sanitized_id = dataset_id.replace("-", "_")
            table_name = f"dataset_{sanitized_id}"
            rows = conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()
            if not rows:
                raise ValueError(f"Dataset table '{table_name}' does not exist.")
            return {row[1]: row[2] for row in rows}
        finally:
            conn.close()

    def get_dataset_metadata(self, dataset_id: str) -> Dict[str, Any]:
        """
        Returns schema, columns_count, and rows_count for the specified dataset.
        """
        conn = self.get_connection()
        try:
            sanitized_id = dataset_id.replace("-", "_")
            table_name = f"dataset_{sanitized_id}"
            
            # Get columns/types
            columns_info = conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()
            if not columns_info:
                raise ValueError(f"Dataset table '{table_name}' does not exist.")
            
            schema = {row[1]: row[2] for row in columns_info}
            columns_count = len(schema)
            
            # Get row count
            rows_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            
            return {
                "schema": schema,
                "columns_count": columns_count,
                "rows_count": rows_count
            }
        finally:
            conn.close()
