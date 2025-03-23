from sqlmodel import SQLModel, Field
from typing import Optional


class DimSupplier(SQLModel, table=True):
    supplier_id: Optional[int] = Field(default=None, primary_key=True)
    supplier_name: str = Field(max_length=50)
    location_id: int = Field(foreign_key="dimlocations.location_id")
