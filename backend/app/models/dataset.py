from pydantic import BaseModel
from typing import Dict

class DatasetMetadata(BaseModel):
    dataset_id: str
    filename: str
    rows_count: int
    columns_count: int
    schema_info: Dict[str, str]
