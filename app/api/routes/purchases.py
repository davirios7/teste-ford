from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.models.purchases import DimPurchases, PurchaseTypeEnum
from app.core.database import get_db
from datetime import date
from sqlalchemy.sql import func
from fastapi.responses import JSONResponse
import json
from app.cache import get_cache, set_cache
from app.utils.serializer import default_serializer

router = APIRouter(prefix="/purchases", tags=["purchases"])


# Listar purchases por tipo e data
@router.get("/by-type-and-date", response_model=List[DimPurchases])
def get_purchases_by_type_and_date(
    purchase_type: PurchaseTypeEnum,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
):
    return db.exec(
        select(DimPurchases).where(
            (DimPurchases.purchase_type == purchase_type)
            & (DimPurchases.purchase_date.between(start_date, end_date))
        )
    ).all()


# Listar purchases por part_id
@router.get("/by-part/{part_id}", response_model=List[DimPurchases])
def get_purchases_by_part(part_id: int, db: Session = Depends(get_db)):
    return db.exec(select(DimPurchases).where(DimPurchases.part_id == part_id)).all()


# Listar purchases por tipo
@router.get("/by-type/{purchase_type}", response_model=List[DimPurchases])
def get_purchases_by_type(
    purchase_type: PurchaseTypeEnum, db: Session = Depends(get_db)
):
    return db.exec(
        select(DimPurchases).where(DimPurchases.purchase_type == purchase_type)
    ).all()

# Listar a quantidade de purchases por ano
@router.get("/count-by-year")
def get_purchase_count_by_year(db: Session = Depends(get_db)):
    stmt = select(
        func.extract("year", DimPurchases.purchase_date).label("year"),
        func.count(DimPurchases.purchase_id),
    ).group_by(func.extract("year", DimPurchases.purchase_date))
    results = db.exec(stmt).all()
    return JSONResponse(content={f"Year {int(r[0])}": r[1] for r in results})


# Listar a quantidade de purchases por mês
@router.get("/count-by-month")
def get_purchase_count_by_month(db: Session = Depends(get_db)):
    stmt = select(
        func.extract("month", DimPurchases.purchase_date).label("month"),
        func.count(DimPurchases.purchase_id),
    ).group_by(func.extract("month", DimPurchases.purchase_date))
    results = db.exec(stmt).all()
    return JSONResponse(content={f"Month {int(r[0])}": r[1] for r in results})


# Listar a quantidade de purchases por tipo
@router.get("/count-by-type")
def get_purchase_count_by_type(db: Session = Depends(get_db)):
    stmt = select(
        DimPurchases.purchase_type, func.count(DimPurchases.purchase_id)
    ).group_by(DimPurchases.purchase_type)
    results = db.exec(stmt).all()
    return JSONResponse(content={r[0]: r[1] for r in results})


# Criar um novo registro em massa
@router.post("/bulk", response_model=List[DimPurchases])
def create_purchase(purchases: List[DimPurchases], db: Session = Depends(get_db)):
    db.add_all(purchases)
    db.commit()
    return purchases


# Criar um único registro
@router.post("/create", response_model=DimPurchases)
def create_purchase(part: DimPurchases, db: Session = Depends(get_db)):
    db.add(part)
    db.commit()
    db.refresh(part)
    return part


# Recuperar todos os registros com paginação
@router.get("", response_model=List[DimPurchases])
async def get_purchases(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    # Gerar chave única para cache com base nos parâmetros de consulta
    cache_key = f"purchases_skip_{skip}_limit_{limit}"

    # Verificar se os dados estão no cache
    cached_data = get_cache(cache_key)
    if cached_data:
        # Se estiver no cache, retorna os dados em cache
        return json.loads(
            cached_data
        )  # Convertendo de volta para o formato esperado (list of DimPurchases)

    # Se não estiver no cache, consulta o banco de dados
    purchases = db.exec(select(DimPurchases).offset(skip).limit(limit)).all()

    # Armazenar os dados no cache por 60 segundos, agora com a serialização correta
    serialized_purchases = json.dumps(
        [purchase.model_dump() for purchase in purchases], default=default_serializer
    )
    set_cache(cache_key, serialized_purchases, expiration=60)

    return purchases


# Recuperar um único registro por ID
@router.get("/{purchase_id}", response_model=DimPurchases)
def get_purchase(purchase_id: int, db: Session = Depends(get_db)):
    purchase = db.get(DimPurchases, purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return purchase


# Atualizar um registro existente
@router.put("/{purchase_id}", response_model=DimPurchases)
def update_purchase(
    purchase_id: int, purchase_data: DimPurchases, db: Session = Depends(get_db)
):
    purchase = db.get(DimPurchases, purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")

    for key, value in purchase_data.model_dump(exclude_unset=True).items():
        setattr(purchase, key, value)

    db.commit()
    db.refresh(purchase)
    return purchase


# Excluir um registro por ID
@router.delete("/{purchase_id}")
def delete_purchase(purchase_id: int, db: Session = Depends(get_db)):
    purchase = db.get(DimPurchases, purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")

    db.delete(purchase)
    db.commit()
    return {"message": "Purchase deleted successfully"}
