from sqlmodel import Session, select
from app.models.parts import DimParts
from typing import List, Optional


# Inserção em massa
def create_parts(session: Session, parts: List[DimParts]) -> None:
    session.bulk_save_objects(parts)
    session.commit()


# Recuperação em massa com paginação
def get_parts(session: Session, chunk_size: int = 1000) -> List[DimParts]:
    return session.exec(select(DimParts).limit(chunk_size)).all()


# Criar um único registro
def create_part(session: Session, part: DimParts) -> DimParts:
    session.add(part)
    session.commit()
    session.refresh(part)
    return part


# Recuperar um único registro por ID
def get_part(session: Session, part_id: int) -> Optional[DimParts]:
    return session.get(DimParts, part_id)


# Atualizar um registro existente
def update_part(
    session: Session, part_id: int, part_data: DimParts
) -> Optional[DimParts]:
    part = session.get(DimParts, part_id)
    if not part:
        return None

    part_data = part_data.model_dump(exclude_unset=True)
    for key, value in part_data.items():
        setattr(part, key, value)

    session.commit()
    session.refresh(part)
    return part


# Excluir um registro por ID
def delete_part(session: Session, part_id: int) -> bool:
    part = session.get(DimParts, part_id)
    if not part:
        return False
    session.delete(part)
    session.commit()
    return True
