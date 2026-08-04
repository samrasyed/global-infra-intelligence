from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Infrastructure
from app.schemas import InfrastructureOut

router = APIRouter(prefix="/api/infrastructure", tags=["infrastructure"])


@router.get("", response_model=list[InfrastructureOut])
def list_infrastructure(db: Session = Depends(get_db), category: str | None = None):
    q = db.query(Infrastructure)
    if category:
        q = q.filter(Infrastructure.category == category)
    return q.all()
