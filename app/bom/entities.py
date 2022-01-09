from dataclasses import dataclass
from typing import Optional


@dataclass
class CSVLineEntity:
    depth: int
    identifier: str
    name: str
    category: Optional[str]
    unit: str
    procurement_type: str
    quantity: float
    price: Optional[float]
