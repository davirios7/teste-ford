from sqlmodel import Session, select
from app.models.purchases import DimPurchases
from typing import List, Optional


# Inserção em massa
def create_purchases(session: Session, purchases: List[DimPurchases]) -> None:
    session.bulk_save_objects(purchases)
    session.commit()


# Recuperação em massa com paginação
def get_purchases(session: Session, chunk_size: int = 1000) -> List[DimPurchases]:
    return session.exec(select(DimPurchases).limit(chunk_size)).all()


# Criar um único registro
def create_purchase(session: Session, purchase: DimPurchases) -> DimPurchases:
    session.add(purchase)
    session.commit()
    session.refresh(purchase)
    return purchase


# Recuperar um único registro por ID
def get_purchase(session: Session, purchase_id: int) -> Optional[DimPurchases]:
    return session.get(DimPurchases, purchase_id)


# Atualizar um registro existente
def update_purchase(
    session: Session, purchase_id: int, purchase_data: DimPurchases
) -> Optional[DimPurchases]:
    purchase = session.get(DimPurchases, purchase_id)
    if not purchase:
        return None

    purchase_data = purchase_data.model_dump(exclude_unset=True)
    for key, value in purchase_data.items():
        setattr(purchase, key, value)

    session.commit()
    session.refresh(purchase)
    return purchase


# Excluir um registro por ID
def delete_purchase(session: Session, purchase_id: int) -> bool:
    purchase = session.get(DimPurchases, purchase_id)
    if not purchase:
        return False
    session.delete(purchase)
    session.commit()
    return True
