from typing import Dict, Optional

_registry: Dict[str, str] = {}

def register_dataset(dataset_id: str, filename: str) -> None:
    _registry[dataset_id] = filename

def get_filename(dataset_id: str) -> Optional[str]:
    return _registry.get(dataset_id)
