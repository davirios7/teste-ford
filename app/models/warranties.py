from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date


class FactWarranties(SQLModel, table=True):
    claim_key: Optional[int] = Field(default=None, primary_key=True)
    vehicle_id: int = Field(foreign_key="dimvehicle.vehicle_id")
    repair_date: date
    client_complaint: Optional[str] = Field(default=None, max_length=65535)
    tech_comment: Optional[str] = Field(default=None, max_length=65535)
    part_id: int = Field(foreign_key="dimparts.part_id")
    classified_issue: Optional[str] = Field(default=None, max_length=50)
    location_id: int = Field(foreign_key="dimlocations.location_id")
    purchase_id: int = Field(foreign_key="dimpurchases.purchase_id")
