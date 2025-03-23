from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date
import enum


class PurchaseTypeEnum(str, enum.Enum):
    NEW = "New"
    USED = "Used"
    REFURBISHED = "Refurbished"


class DimPurchases(SQLModel, table=True):
    purchase_id: Optional[int] = Field(default=None, primary_key=True)
    purchase_type: PurchaseTypeEnum
    purchase_date: date
    part_id: int = Field(foreign_key="dimparts.part_id")
