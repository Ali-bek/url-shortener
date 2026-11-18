from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import LinkCreate, LinkOut, LinkStats, LinkUpdate

router = APIRouter(prefix="/api/links", tags=["links"])

RESERVED_CODES = {"api", "docs", "redoc"}


def get_link_or_404(db: Session, code: str):
    link = crud.get_link_by_code(db, code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return link


@router.post("", response_model=LinkOut, status_code=201)
def create_link(payload: LinkCreate, db: Session = Depends(get_db)):
    code = payload.custom_code
    if code and (code.lower() in RESERVED_CODES or crud.get_link_by_code(db, code)):
        raise HTTPException(status_code=409, detail="This code is not available")
    return crud.create_link(db, str(payload.original_url), code)


@router.get("", response_model=list[LinkOut])
def list_links(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return crud.list_links(db, skip, limit)


@router.get("/{code}", response_model=LinkOut)
def read_link(code: str, db: Session = Depends(get_db)):
    return get_link_or_404(db, code)


@router.patch("/{code}", response_model=LinkOut)
def update_link(code: str, payload: LinkUpdate, db: Session = Depends(get_db)):
    link = get_link_or_404(db, code)
    return crud.update_link(db, link, str(payload.original_url))


@router.delete("/{code}", status_code=204)
def delete_link(code: str, db: Session = Depends(get_db)):
    crud.delete_link(db, get_link_or_404(db, code))


@router.get("/{code}/stats", response_model=LinkStats)
def link_stats(code: str, db: Session = Depends(get_db)):
    return crud.get_stats(db, get_link_or_404(db, code))