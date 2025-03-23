from sqlmodel import SQLModel, Field
from typing import Optional
import enum


class MarketEnum(str, enum.Enum):
    DOMESTIC = "Domestic"
    INTERNATIONAL = "International"


class DimLocations(SQLModel, table=True):
    location_id: Optional[int] = Field(default=None, primary_key=True)
    market: MarketEnum
    country: str = Field(max_length=50)
    province: str = Field(max_length=50)
    city: str = Field(max_length=50)
