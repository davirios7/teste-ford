from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.models.parts import DimParts
from app.core.database import get_db
from sqlalchemy.sql import func
from fastapi.responses import JSONResponse
import json
from app.cache import get_cache, set_cache
from app.utils.serializer import default_serializer


router = APIRouter(prefix="/parts", tags=["parts"])


# Listar peças associadas a uma última compra
@router.get("/by-purchase/{last_id_purchase}", response_model=List[DimParts])
def get_parts_by_purchase(last_id_purchase: int, db: Session = Depends(get_db)):
    return db.exec(
        select(DimParts).where(DimParts.last_id_purchase == last_id_purchase)
    ).all()


# Listar todas as peças de um fornecedor que foram compradas pelo menos uma vez
@router.get("/purchased-by-supplier/{supplier_id}", response_model=List[DimParts])
def get_purchased_parts_by_supplier(supplier_id: int, db: Session = Depends(get_db)):
    return db.exec(
        select(DimParts).where(
            DimParts.supplier_id == supplier_id, DimParts.last_id_purchase.isnot(None)
        )
    ).all()


# Listar todas as peças de um fornecedor
@router.get("/by-supplier/{supplier_id}", response_model=List[DimParts])
def get_parts_by_supplier(supplier_id: int, db: Session = Depends(get_db)):
    return db.exec(select(DimParts).where(DimParts.supplier_id == supplier_id)).all()


# Listar todas as peças que foram compradas pelo menos uma vez
@router.get("/purchased", response_model=List[DimParts])
def get_purchased_parts(db: Session = Depends(get_db)):
    return db.exec(select(DimParts).where(DimParts.last_id_purchase.isnot(None))).all()


# Contar quantas compras foram feitas por fornecedor
@router.get("/count-purchases-by-supplier")
def count_purchases_by_supplier(db: Session = Depends(get_db)):
    stmt = select(DimParts.supplier_id, func.count(DimParts.last_id_purchase)).group_by(
        DimParts.supplier_id
    )
    results = db.exec(stmt).all()
    return JSONResponse(content={str(r[0]): r[1] for r in results})


# Listar peças por fornecedor
@router.get("/count-by-supplier")
def count_parts_by_supplier(db: Session = Depends(get_db)):
    stmt = select(DimParts.supplier_id, func.count(DimParts.part_id)).group_by(
        DimParts.supplier_id
    )
    results = db.exec(stmt).all()
    return JSONResponse(content={str(r[0]): r[1] for r in results})


# Contar quantas peças diferentes já foram compradas pelo menos uma vez
@router.get("/count-purchased")
def count_purchased_parts(db: Session = Depends(get_db)):
    total_purchased = db.exec(
        select(func.count(func.distinct(DimParts.part_id))).where(
            DimParts.last_id_purchase.isnot(None)
        )
    ).one()
    return JSONResponse(content={"total_purchased_parts": total_purchased})


# Listar o número total de peças
@router.get("/count")
def count_parts(db: Session = Depends(get_db)):
    total_parts = db.exec(select(func.count(DimParts.part_id))).one()
    return JSONResponse(content={"total_parts": total_parts})


# Inserção em massa
@router.post("/bulk")
def create_parts(parts: List[DimParts], db: Session = Depends(get_db)):
    db.bulk_save_objects(parts)
    db.commit()
    return {"message": "Bulk parts created successfully"}


# Criar um único registro
@router.post("/create", response_model=DimParts)
def create_part(part: DimParts, db: Session = Depends(get_db)):
    db.add(part)
    db.commit()
    db.refresh(part)
    return part


# Recuperação em massa com paginação
@router.get("", response_model=List[DimParts])
async def get_parts(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    # Gerar chave única para cache com base nos parâmetros de consulta
    cache_key = f"parts_skip_{skip}_limit_{limit}"

    # Verificar se os dados estão no cache
    cached_data = get_cache(cache_key)
    if cached_data:
        # Se estiver no cache, retorna os dados em cache
        return json.loads(
            cached_data
        )  # Convertendo de volta para o formato esperado (list of DimParts)

    # Se não estiver no cache, consulta o banco de dados
    parts = db.exec(select(DimParts).offset(skip).limit(limit)).all()

    # Armazenar os dados no cache por 60 segundos, agora com a serialização correta
    serialized_parts = json.dumps(
        [part.model_dump() for part in parts], default=default_serializer
    )
    set_cache(cache_key, serialized_parts, expiration=60)

    return parts


# Recuperar um único registro por ID
@router.get("/{part_id}", response_model=DimParts)
def get_part(part_id: int, db: Session = Depends(get_db)):
    part = db.get(DimParts, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    return part


# Atualizar um registro existente
@router.put("/{part_id}", response_model=DimParts)
def update_part(part_id: int, part_data: DimParts, db: Session = Depends(get_db)):
    part = db.get(DimParts, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    for key, value in part_data.model_dump(exclude_unset=True).items():
        setattr(part, key, value)

    db.commit()
    db.refresh(part)
    return part


# Excluir um registro por ID
@router.delete("/{part_id}")
def delete_part(part_id: int, db: Session = Depends(get_db)):
    part = db.get(DimParts, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    db.delete(part)
    db.commit()
    return {"message": "Part deleted successfully"}
