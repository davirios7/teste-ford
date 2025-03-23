from sqlmodel import SQLModel, Field
from typing import Optional


class DimParts(SQLModel, table=True):
    part_id: Optional[int] = Field(default=None, primary_key=True)
    part_name: str = Field(index=True, max_length=255)
    last_id_purchase: int
    supplier_id: int
