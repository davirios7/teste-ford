from sqlmodel import Session, select
from app.models.locations import DimLocations
from typing import List, Optional


# Inserção em massa
def create_locations(db: Session, locations: List[DimLocations]) -> None:
    db.bulk_save_objects(locations)
    db.commit()


# Recuperação em massa com paginação
def get_locations(db: Session, chunk_size: int = 1000) -> List[DimLocations]:
    return db.exec(select(DimLocations).limit(chunk_size)).all()


# Criar um único registro
def create_location(db: Session, location: DimLocations) -> DimLocations:
    db.add(location)
    db.commit()
    db.refresh(location)
    return location


# Recuperar um único registro por ID
def get_location(db: Session, location_id: int) -> Optional[DimLocations]:
    return db.get(DimLocations, location_id)


# Atualizar um registro existente
def update_location(
    db: Session, location_id: int, location_data: DimLocations
) -> Optional[DimLocations]:
    location = db.get(DimLocations, location_id)
    if not location:
        return None
    for key, value in location_data.model_dump(exclude_unset=True).items():
        setattr(location, key, value)
    db.commit()
    db.refresh(location)
    return location


# Excluir um registro por ID
def delete_location(db: Session, location_id: int) -> bool:
    location = db.get(DimLocations, location_id)
    if not location:
        return False
    db.delete(location)
    db.commit()
    return True
