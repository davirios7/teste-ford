from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date
from enum import Enum


# Definição do ENUM para tipos de propulsão
class PropulsionType(str, Enum):
    GASOLINE = "Gasoline"
    DIESEL = "Diesel"
    ELECTRIC = "Electric"
    HYBRID = "Hybrid"


# Modelo DimVehicle com ENUM
class DimVehicle(SQLModel, table=True):
    vehicle_id: Optional[int] = Field(default=None, primary_key=True)
    model: str = Field(index=True, max_length=255)
    prod_date: date
    year: int
    propulsion: PropulsionType
