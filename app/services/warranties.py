from sqlmodel import Session, select
from app.models.warranties import FactWarranties
from typing import List, Optional


# Inserção em massa
def create_warranties(session: Session, warranties: List[FactWarranties]) -> None:
    session.bulk_save_objects(warranties)
    session.commit()


# Recuperação em massa com paginação
def get_warranties(session: Session, chunk_size: int = 1000) -> List[FactWarranties]:
    return session.exec(select(FactWarranties).limit(chunk_size)).all()


# Criar um único registro
def create_warranty(session: Session, warranty: FactWarranties) -> FactWarranties:
    session.add(warranty)
    session.commit()
    session.refresh(warranty)
    return warranty


# Recuperar um único registro por claim_key
def get_warranty(session: Session, claim_key: int) -> Optional[FactWarranties]:
    return session.get(FactWarranties, claim_key)


# Atualizar um registro existente
def update_warranty(
    session: Session, claim_key: int, warranty_data: FactWarranties
) -> Optional[FactWarranties]:
    warranty = session.get(FactWarranties, claim_key)
    if not warranty:
        return None

    warranty_data = warranty_data.model_dump(exclude_unset=True)
    for key, value in warranty_data.items():
        setattr(warranty, key, value)

    session.commit()
    session.refresh(warranty)
    return warranty


# Excluir um registro por claim_key
def delete_warranty(session: Session, claim_key: int) -> bool:
    warranty = session.get(FactWarranties, claim_key)
    if not warranty:
        return False
    session.delete(warranty)
    session.commit()
    return True
