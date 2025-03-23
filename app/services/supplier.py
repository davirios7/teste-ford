from sqlmodel import Session, select
from app.models.supplier import DimSupplier
from typing import List, Optional


# Inserção em massa
def create_suppliers(session: Session, suppliers: List[DimSupplier]) -> None:
    session.bulk_save_objects(suppliers)
    session.commit()


# Recuperação em massa com paginação
def get_suppliers(session: Session, chunk_size: int = 1000) -> List[DimSupplier]:
    return session.exec(select(DimSupplier).limit(chunk_size)).all()


# Criar um único registro
def create_supplier(session: Session, supplier: DimSupplier) -> DimSupplier:
    session.add(supplier)
    session.commit()
    session.refresh(supplier)
    return supplier


# Recuperar um único registro por ID
def get_supplier(session: Session, supplier_id: int) -> Optional[DimSupplier]:
    return session.get(DimSupplier, supplier_id)


# Atualizar um registro existente
def update_supplier(
    session: Session, supplier_id: int, supplier_data: DimSupplier
) -> Optional[DimSupplier]:
    supplier = session.get(DimSupplier, supplier_id)
    if not supplier:
        return None

    supplier_data = supplier_data.model_dump(exclude_unset=True)
    for key, value in supplier_data.items():
        setattr(supplier, key, value)

    session.commit()
    session.refresh(supplier)
    return supplier


# Excluir um registro por ID
def delete_supplier(session: Session, supplier_id: int) -> bool:
    supplier = session.get(DimSupplier, supplier_id)
    if not supplier:
        return False
    session.delete(supplier)
    session.commit()
    return True
