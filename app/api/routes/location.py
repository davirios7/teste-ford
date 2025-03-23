from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.models.locations import DimLocations, MarketEnum
from app.core.database import get_db
from sqlalchemy.sql import func
from fastapi.responses import JSONResponse
from app.utils.serializer import default_serializer
import json
from app.cache import get_cache, set_cache

router = APIRouter(prefix="/locations", tags=["locations"])


# Listar por tipo de mercado
@router.get("/by-market/{market_type}", response_model=List[DimLocations])
def get_locations_by_market(market_type: MarketEnum, db: Session = Depends(get_db)):
    return db.exec(select(DimLocations).where(DimLocations.market == market_type)).all()


# Listar todas as cidades cadastradas de um país
@router.get("/cities/{country}", response_model=List[str])
def get_cities_by_country(country: str, db: Session = Depends(get_db)):
    stmt = select(DimLocations.city).where(DimLocations.country == country)
    return db.exec(stmt).all()


# Listar todas as províncias de um país
@router.get("/provinces/{country}", response_model=List[str])
def get_provinces_by_country(country: str, db: Session = Depends(get_db)):
    stmt = (
        select(DimLocations.province).where(DimLocations.country == country).distinct()
    )
    return db.exec(stmt).all()


# Listar todas as cidades dentro de uma província
@router.get("/cities/{country}/{province}", response_model=List[str])
def get_cities_by_province(country: str, province: str, db: Session = Depends(get_db)):
    stmt = (
        select(DimLocations.city)
        .where(DimLocations.country == country, DimLocations.province == province)
        .distinct()
    )
    return db.exec(stmt).all()


# Listar quantidade por país
@router.get("/count-by-country")
def get_location_count_by_country(db: Session = Depends(get_db)):
    stmt = select(DimLocations.country, func.count(DimLocations.location_id)).group_by(
        DimLocations.country
    )
    results = db.exec(stmt).all()
    return JSONResponse(content={r[0]: r[1] for r in results})


# Listar quantas cidades únicas há por país
@router.get("/unique-cities-by-country")
def get_unique_cities_by_country(db: Session = Depends(get_db)):
    stmt = select(
        DimLocations.country, func.count(func.distinct(DimLocations.city))
    ).group_by(DimLocations.country)
    results = db.exec(stmt).all()
    return JSONResponse(content={r[0]: r[1] for r in results})


# Contar quantas províncias há por país
@router.get("/count-provinces-by-country")
def get_province_count_by_country(db: Session = Depends(get_db)):
    stmt = select(
        DimLocations.country, func.count(func.distinct(DimLocations.province))
    ).group_by(DimLocations.country)
    results = db.exec(stmt).all()
    return JSONResponse(content={r[0]: r[1] for r in results})


# Contar quantos locais há por tipo de mercado (Doméstico/Internacional)
@router.get("/count-by-market")
def get_location_count_by_market(db: Session = Depends(get_db)):
    stmt = select(DimLocations.market, func.count()).group_by(DimLocations.market)
    results = db.exec(stmt).all()
    return JSONResponse(content={r[0]: r[1] for r in results})


# Inserção em massa
@router.post("/bulk")
def create_locations(locations: List[DimLocations], db: Session = Depends(get_db)):
    db.bulk_save_objects(locations)
    db.commit()
    return {"message": "Bulk locations created successfully"}


# Criar um único registro
@router.post("/create", response_model=DimLocations)
def create_location(location: DimLocations, db: Session = Depends(get_db)):
    db.add(location)
    db.commit()
    db.refresh(location)
    return location


# Recuperação em massa com paginação
@router.get("", response_model=List[DimLocations])
async def get_locations(
    skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)
):
    # Gerar chave única para cache com base nos parâmetros de consulta
    cache_key = f"locations_skip_{skip}_limit_{limit}"

    # Verificar se os dados estão no cache
    cached_data = get_cache(cache_key)
    if cached_data:
        # Se estiver no cache, retorna os dados em cache
        return json.loads(
            cached_data
        )  # Convertendo de volta para o formato esperado (list of DimLocations)

    # Se não estiver no cache, consulta o banco de dados
    locations = db.exec(select(DimLocations).offset(skip).limit(limit)).all()

    # Armazenar os dados no cache por 60 segundos, agora com a serialização correta
    serialized_locations = json.dumps(
        [location.model_dump() for location in locations], default=default_serializer
    )
    set_cache(cache_key, serialized_locations, expiration=60)

    return locations


# Recuperar um único registro por ID
@router.get("/{location_id}", response_model=DimLocations)
def get_location(location_id: int, db: Session = Depends(get_db)):
    location = db.get(DimLocations, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


# Atualizar um registro existente
@router.put("/{location_id}", response_model=DimLocations)
def update_location(
    location_id: int, location_data: DimLocations, db: Session = Depends(get_db)
):
    location = db.get(DimLocations, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    for key, value in location_data.model_dump(exclude_unset=True).items():
        setattr(location, key, value)

    db.commit()
    db.refresh(location)
    return location


# Excluir um registro por ID
@router.delete("/{location_id}")
def delete_location(location_id: int, db: Session = Depends(get_db)):
    location = db.get(DimLocations, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    db.delete(location)
    db.commit()
    return {"message": "Location deleted successfully"}
