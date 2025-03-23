from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.models.warranties import FactWarranties
from app.core.database import get_db
from sqlalchemy.sql import func
from fastapi.responses import JSONResponse
from datetime import date
import json
from app.cache import get_cache, set_cache
from app.utils.serializer import default_serializer
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/warranties", tags=["warranties"])


# Listar warranties por intervalo de datas
@router.get("/by-date-range", response_model=List[FactWarranties])
def get_warranties_by_date_range(
    start_date: date, end_date: date, db: Session = Depends(get_db)
):
    stmt = select(FactWarranties).where(
        (FactWarranties.repair_date >= start_date)
        & (FactWarranties.repair_date <= end_date)
    )
    return db.exec(stmt).all()


# Listar warranties por vehicle_id
@router.get("/by-vehicle/{vehicle_id}", response_model=List[FactWarranties])
def get_warranties_by_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    return db.exec(
        select(FactWarranties).where(FactWarranties.vehicle_id == vehicle_id)
    ).all()


# Listar warranties por part_id
@router.get("/by-part/{part_id}", response_model=List[FactWarranties])
def get_warranties_by_part(part_id: int, db: Session = Depends(get_db)):
    return db.exec(
        select(FactWarranties).where(FactWarranties.part_id == part_id)
    ).all()


# Listar warranties por localização
@router.get("/by-location/{location_id}", response_model=List[FactWarranties])
def get_warranties_by_location(location_id: int, db: Session = Depends(get_db)):
    return db.exec(
        select(FactWarranties).where(FactWarranties.location_id == location_id)
    ).all()


# Listar a quantidade de warranties por vehicle_id
@router.get("/count-by-vehicle")
def count_warranties_by_vehicle(db: Session = Depends(get_db)):
    stmt = select(
        FactWarranties.vehicle_id, func.count(FactWarranties.claim_key)
    ).group_by(FactWarranties.vehicle_id)
    results = db.exec(stmt).all()
    return JSONResponse(content={r[0]: r[1] for r in results})


# Listar a quantidade de warranties por part_id
@router.get("/count-by-part")
def count_warranties_by_part(db: Session = Depends(get_db)):
    stmt = select(
        FactWarranties.part_id, func.count(FactWarranties.claim_key)
    ).group_by(FactWarranties.part_id)
    results = db.exec(stmt).all()
    return JSONResponse(content={r[0]: r[1] for r in results})


# Listar a quantidade de warranties por localização
@router.get("/count-by-location")
def count_warranties_by_location(db: Session = Depends(get_db)):
    stmt = select(
        FactWarranties.location_id, func.count(FactWarranties.claim_key)
    ).group_by(FactWarranties.location_id)
    results = db.exec(stmt).all()
    return JSONResponse(content={r[0]: r[1] for r in results})


# Listar a quantidade de warranties por ano
@router.get("/count-by-year")
def count_warranties_by_year(db: Session = Depends(get_db)):
    stmt = select(
        func.extract("year", FactWarranties.repair_date).label("year"),
        func.count(FactWarranties.claim_key),
    ).group_by(func.extract("year", FactWarranties.repair_date))
    results = db.exec(stmt).all()
    return JSONResponse(content={f"Year {int(r[0])}": r[1] for r in results})


# Inserção em massa
@router.post("/bulk")
def create_warranties(warranties: List[FactWarranties], db: Session = Depends(get_db)):
    db.bulk_save_objects(warranties)
    db.commit()
    return {"message": "Bulk warranties created successfully"}


# Criar um único registro
@router.post("/create", response_model=FactWarranties)
def create_warranty(warranty: FactWarranties, db: Session = Depends(get_db)):
    db.add(warranty)
    db.commit()
    db.refresh(warranty)
    return warranty


# Recuperação em massa com paginação
@router.get("", response_model=List[FactWarranties])
async def get_warranties(
    skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)
):
    # Gerar chave única para cache com base nos parâmetros de consulta
    cache_key = f"warranties_skip_{skip}_limit_{limit}"

    # Verificar se os dados estão no cache
    cached_data = get_cache(cache_key)
    if cached_data:
        # Se estiver no cache, retorna os dados em cache
        return json.loads(
            cached_data
        )  # Convertendo de volta para o formato esperado (list of FactWarranties)

    # Se não estiver no cache, consulta o banco de dados
    warranties = db.exec(select(FactWarranties).offset(skip).limit(limit)).all()

    # Armazenar os dados no cache por 60 segundos, agora com a serialização correta
    serialized_warranties = json.dumps(
        [
            jsonable_encoder(
                warranty, custom_encoder={FactWarranties: default_serializer}
            )
            for warranty in warranties
        ]
    )
    set_cache(cache_key, serialized_warranties, expiration=60)

    return warranties


# Recuperar um único registro por claim_key
@router.get("/{claim_key}", response_model=FactWarranties)
def get_warranty(claim_key: int, db: Session = Depends(get_db)):
    warranty = db.get(FactWarranties, claim_key)
    if not warranty:
        raise HTTPException(status_code=404, detail="Warranty not found")
    return warranty


# Atualizar um registro existente
@router.put("/{claim_key}", response_model=FactWarranties)
def update_warranty(
    claim_key: int, warranty_data: FactWarranties, db: Session = Depends(get_db)
):
    warranty = db.get(FactWarranties, claim_key)
    if not warranty:
        raise HTTPException(status_code=404, detail="Warranty not found")

    warranty_data = warranty_data.model_dump(exclude_unset=True)
    for key, value in warranty_data.items():
        setattr(warranty, key, value)

    db.commit()
    db.refresh(warranty)
    return warranty


# Excluir um registro por claim_key
@router.delete("/{claim_key}")
def delete_warranty(claim_key: int, db: Session = Depends(get_db)):
    warranty = db.get(FactWarranties, claim_key)
    if not warranty:
        raise HTTPException(status_code=404, detail="Warranty not found")

    db.delete(warranty)
    db.commit()
    return {"message": "Warranty deleted successfully"}
