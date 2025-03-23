from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from app.models.supplier import DimSupplier
from app.models.locations import DimLocations
from app.core.database import get_db
from fastapi.responses import JSONResponse
from sqlalchemy.sql import func
import json
from app.cache import get_cache, set_cache
from app.utils.serializer import default_serializer


router = APIRouter(prefix="/suppliers", tags=["suppliers"])


# Listar suppliers por localização
@router.get("/by-location/{location_id}", response_model=List[DimSupplier])
def get_suppliers_by_location(location_id: int, db: Session = Depends(get_db)):
    return db.exec(
        select(DimSupplier).where(DimSupplier.location_id == location_id)
    ).all()


# Listar suppliers por país (usando DimLocations)
@router.get("/by-country/{country}", response_model=List[DimSupplier])
def get_suppliers_by_country(country: str, db: Session = Depends(get_db)):
    stmt = select(DimSupplier).join(DimLocations).where(DimLocations.country == country)
    return db.exec(stmt).all()


# Listar suppliers por província (usando DimLocations)
@router.get("/by-province/{province}", response_model=List[DimSupplier])
def get_suppliers_by_province(province: str, db: Session = Depends(get_db)):
    stmt = (
        select(DimSupplier).join(DimLocations).where(DimLocations.province == province)
    )
    return db.exec(stmt).all()


# Quantidade de suppliers únicos por país
@router.get("/unique-suppliers-by-country")
def get_unique_suppliers_by_country(db: Session = Depends(get_db)):
    stmt = (
        select(DimLocations.country, func.count(func.distinct(DimSupplier.supplier_id)))
        .join(DimSupplier, DimSupplier.location_id == DimLocations.location_id)
        .group_by(DimLocations.country)
    )
    results = db.exec(stmt).all()
    return JSONResponse(content={r[0]: r[1] for r in results})


# Localizações com mais suppliers
@router.get("/top-locations")
def get_top_supplier_locations(db: Session = Depends(get_db)):
    stmt = (
        select(
            DimSupplier.location_id, func.count(DimSupplier.supplier_id).label("count")
        )
        .group_by(DimSupplier.location_id)
        .order_by(func.count(DimSupplier.supplier_id).desc())
        .limit(5)
    )
    results = db.exec(stmt).all()
    return results


# Número de suppliers por localização
@router.get("/count-suppliers-per-location")
def count_suppliers_per_location(db: Session = Depends(get_db)):
    stmt = (
        select(
            DimLocations.location_id,
            func.count(DimSupplier.supplier_id).label("supplier_count"),
        )
        .join(DimSupplier, DimSupplier.location_id == DimLocations.location_id)
        .group_by(DimLocations.location_id)
    )
    results = db.exec(stmt).all()
    return JSONResponse(content={r[0]: r[1] for r in results})


# Quantidade de suppliers por localização
@router.get("/count-by-location")
def get_supplier_count_by_location(db: Session = Depends(get_db)):
    stmt = select(
        DimSupplier.location_id, func.count(DimSupplier.supplier_id)
    ).group_by(DimSupplier.location_id)
    results = db.exec(stmt).all()
    return JSONResponse(content={r[0]: r[1] for r in results})


# Listar suppliers por nome
@router.get("/search", response_model=List[DimSupplier])
def search_suppliers(name: str, db: Session = Depends(get_db)):
    return db.exec(
        select(DimSupplier).where(DimSupplier.supplier_name.contains(name))
    ).all()


# Inserção em massa
@router.post("/bulk")
def create_suppliers(suppliers: List[DimSupplier], db: Session = Depends(get_db)):
    db.bulk_save_objects(suppliers)
    db.commit()
    return {"message": "Bulk suppliers created successfully"}


# Criar um único registro
@router.post("/create", response_model=DimSupplier)
def create_supplier(supplier: DimSupplier, db: Session = Depends(get_db)):
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


# Recuperação em massa com paginação
@router.get("", response_model=List[DimSupplier])
async def get_suppliers(
    skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)
):
    # Gerar chave única para cache com base nos parâmetros de consulta
    cache_key = f"suppliers_skip_{skip}_limit_{limit}"

    # Verificar se os dados estão no cache
    cached_data = get_cache(cache_key)
    if cached_data:
        # Se estiver no cache, retorna os dados em cache
        return json.loads(
            cached_data
        )  # Convertendo de volta para o formato esperado (list of DimSupplier)

    # Se não estiver no cache, consulta o banco de dados
    suppliers = db.exec(select(DimSupplier).offset(skip).limit(limit)).all()

    # Armazenar os dados no cache por 60 segundos, agora com a serialização correta
    serialized_suppliers = json.dumps(
        [supplier.model_dump() for supplier in suppliers], default=default_serializer
    )
    set_cache(cache_key, serialized_suppliers, expiration=60)

    return suppliers


# Recuperar um único registro por ID
@router.get("/{supplier_id}", response_model=DimSupplier)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.get(DimSupplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


# Atualizar um registro existente
@router.put("/{supplier_id}", response_model=DimSupplier)
def update_supplier(
    supplier_id: int, supplier_data: DimSupplier, db: Session = Depends(get_db)
):
    supplier = db.get(DimSupplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    supplier_data = supplier_data.model_dump(exclude_unset=True)
    for key, value in supplier_data.items():
        setattr(supplier, key, value)

    db.commit()
    db.refresh(supplier)
    return supplier


# Excluir um registro por ID
@router.delete("/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.get(DimSupplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    db.delete(supplier)
    db.commit()
    return {"message": "Supplier deleted successfully"}
