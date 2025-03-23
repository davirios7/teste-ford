from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.core.database import get_db
from app.models.vehicle import DimVehicle, PropulsionType
from sqlalchemy.sql import func
from fastapi.responses import JSONResponse
from datetime import date
from app.cache import get_cache, set_cache
import json
from app.utils.serializer import default_serializer

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


# Listar vehicles pela data de produção
@router.get("/by-prod-date-range", response_model=List[DimVehicle])
def get_vehicles_by_prod_date_range(
    start_date: date, end_date: date, db: Session = Depends(get_db)
):
    stmt = select(DimVehicle).where(
        (DimVehicle.prod_date >= start_date) & (DimVehicle.prod_date <= end_date)
    )
    return db.exec(stmt).all()


# Listar vehicles por modelo
@router.get("/by-model/{model}", response_model=List[DimVehicle])
def get_vehicles_by_model(model: str, db: Session = Depends(get_db)):
    return db.exec(select(DimVehicle).where(DimVehicle.model.contains(model))).all()


# Listar vehicles por tipo de propulsão
@router.get("/by-propulsion/{propulsion_type}", response_model=List[DimVehicle])
def get_vehicles_by_propulsion(
    propulsion_type: PropulsionType, db: Session = Depends(get_db)
):
    return db.exec(
        select(DimVehicle).where(DimVehicle.propulsion == propulsion_type)
    ).all()


# Listar vehicles por ano de fabricação
@router.get("/by-year/{year}", response_model=List[DimVehicle])
def get_vehicles_by_year(year: int, db: Session = Depends(get_db)):
    return db.exec(select(DimVehicle).where(DimVehicle.year == year)).all()


# Listar quantidade de vehicles por faixa de ano
@router.get("/count-by-year-range")
def count_vehicles_by_year_range(
    start_year: int, end_year: int, db: Session = Depends(get_db)
):
    stmt = (
        select(DimVehicle.year, func.count(DimVehicle.vehicle_id))
        .where(DimVehicle.year >= start_year, DimVehicle.year <= end_year)
        .group_by(DimVehicle.year)
    )
    results = db.exec(stmt).all()
    return JSONResponse(content={r[0]: r[1] for r in results})


# Listar quantidade de vehicles por tipo de propulsão
@router.get("/count-by-propulsion")
def count_vehicles_by_propulsion(db: Session = Depends(get_db)):
    stmt = select(DimVehicle.propulsion, func.count(DimVehicle.vehicle_id)).group_by(
        DimVehicle.propulsion
    )
    results = db.exec(stmt).all()
    return JSONResponse(content={r[0]: r[1] for r in results})


# Listar quantidade de vehicles por ano de fabricação
@router.get("/count-by-year")
def count_vehicles_by_year(db: Session = Depends(get_db)):
    stmt = select(DimVehicle.year, func.count(DimVehicle.vehicle_id)).group_by(
        DimVehicle.year
    )
    results = db.exec(stmt).all()
    return JSONResponse(content={r[0]: r[1] for r in results})


# Listar a quantidade de vehicles por mês de produção
@router.get("/count-by-prod-month")
def count_vehicles_by_prod_month(db: Session = Depends(get_db)):
    stmt = select(
        func.extract("month", DimVehicle.prod_date), func.count(DimVehicle.vehicle_id)
    ).group_by(func.extract("month", DimVehicle.prod_date))
    results = db.exec(stmt).all()
    return JSONResponse(content={f"Month {int(r[0])}": r[1] for r in results})


# Inserção em massa
@router.post("/bulk")
def create_vehicles(vehicles: List[DimVehicle], db: Session = Depends(get_db)):
    db.bulk_save_objects(vehicles)
    db.commit()
    return {"message": "Bulk vehicles created successfully"}


# Criar um único registro
@router.post("/create", response_model=DimVehicle)
def create_vehicle(vehicle: DimVehicle, db: Session = Depends(get_db)):
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


# Recuperação em massa com paginação
@router.get("", response_model=List[DimVehicle])
async def get_vehicles(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    # Gerar chave única para cache com base nos parâmetros de consulta
    cache_key = f"vehicles_skip_{skip}_limit_{limit}"

    # Verificar se os dados estão no cache
    cached_data = get_cache(cache_key)
    if cached_data:
        # Se estiver no cache, retorna os dados em cache
        return json.loads(
            cached_data
        )  # Convertendo de volta para o formato esperado (list of DimVehicle)

    # Se não estiver no cache, consulta o banco de dados
    vehicles = db.exec(select(DimVehicle).offset(skip).limit(limit)).all()

    # Armazenar os dados no cache por 60 segundos, agora com a serialização correta
    serialized_vehicles = json.dumps(
        [vehicle.model_dump() for vehicle in vehicles], default=default_serializer
    )
    set_cache(cache_key, serialized_vehicles, expiration=60)

    return vehicles


# Recuperar um único registro por ID
@router.get("/{vehicle_id}", response_model=DimVehicle)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.get(DimVehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


# Atualizar um registro existente
@router.put("/{vehicle_id}", response_model=DimVehicle)
def update_vehicle(
    vehicle_id: int, vehicle_data: DimVehicle, db: Session = Depends(get_db)
):
    vehicle = db.get(DimVehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    vehicle_data = vehicle_data.model_dump(exclude_unset=True)
    for key, value in vehicle_data.items():
        setattr(vehicle, key, value)

    db.commit()
    db.refresh(vehicle)
    return vehicle


# Excluir um registro por ID
@router.delete("/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.get(DimVehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    db.delete(vehicle)
    db.commit()
    return {"message": "Vehicle deleted successfully"}
