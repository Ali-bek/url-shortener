from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.crud import get_link_by_code, record_click
from app.database import get_db

router = APIRouter(tags=["redirect"])


@router.get("/{code}", include_in_schema=False)
def redirect(code: str, request: Request, db: Session = Depends(get_db)):
    link = get_link_by_code(db, code)
    if not link:
        raise HTTPException(status_code=404, detail="Short link not found")

    record_click(
        db,
        link,
        user_agent=request.headers.get("user-agent"),
        referrer=request.headers.get("referer"),
    )
    # 307 (temporary) so browsers don't cache the redirect and skip our click tracking
    return RedirectResponse(link.original_url, status_code=307)