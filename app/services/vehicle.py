from sqlmodel import Session, select
from app.models.vehicle import DimVehicle
from typing import List, Optional


# Inserção em massa
def create_vehicles(session: Session, vehicles: List[DimVehicle]) -> None:
    session.bulk_save_objects(vehicles)
    session.commit()


# Recuperação em massa com paginação
def get_vehicles(session: Session, chunk_size: int = 1000) -> List[DimVehicle]:
    return session.exec(select(DimVehicle).limit(chunk_size)).all()


# Criar um único registro
def create_vehicle(session: Session, vehicle: DimVehicle) -> DimVehicle:
    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)
    return vehicle


# Recuperar um único registro por ID
def get_vehicle(session: Session, vehicle_id: int) -> Optional[DimVehicle]:
    return session.get(DimVehicle, vehicle_id)


# Atualizar um registro existente
def update_vehicle(
    session: Session, vehicle_id: int, vehicle_data: DimVehicle
) -> Optional[DimVehicle]:
    vehicle = session.get(DimVehicle, vehicle_id)
    if not vehicle:
        return None

    vehicle_data = vehicle_data.model_dump(exclude_unset=True)
    for key, value in vehicle_data.items():
        setattr(vehicle, key, value)

    session.commit()
    session.refresh(vehicle)
    return vehicle


# Excluir um registro por ID
def delete_vehicle(session: Session, vehicle_id: int) -> bool:
    vehicle = session.get(DimVehicle, vehicle_id)
    if not vehicle:
        return False
    session.delete(vehicle)
    session.commit()
    return True
