from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Click, Link
from app.utils import generate_code


def get_link_by_code(db: Session, code: str) -> Link | None:
    return db.scalar(select(Link).where(Link.code == code))


def list_links(db: Session, skip: int = 0, limit: int = 50) -> list[Link]:
    stmt = select(Link).order_by(Link.created_at.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt))


def _unique_code(db: Session) -> str:
    while True:
        code = generate_code()
        if not get_link_by_code(db, code):
            return code


def create_link(db: Session, original_url: str, custom_code: str | None) -> Link:
    link = Link(code=custom_code or _unique_code(db), original_url=original_url)
    
    db.add(link)
    db.commit()
    
    # Refresh the objet to generate 'created_at' && 'id'
    db.refresh(link)
    
    return link


def update_link(db: Session, link: Link, original_url: str) -> Link:
    link.original_url = original_url
    db.commit()

    # Refresh link objet data
    db.refresh(link)
    return link


def delete_link(db: Session, link: Link) -> None:
    db.delete(link)
    db.commit()


def record_click(
    db: Session, link: Link, user_agent: str | None, referrer: str | None
) -> None:
    db.add(
        Click(
            link_id=link.id,
            user_agent=(user_agent or "")[:500] or None,
            referrer=(referrer or "")[:500] or None,
        )
    )
    db.commit()


def get_stats(db: Session, link: Link) -> dict:
    # total clicks of a given link 
    total = db.scalar(select(func.count(Click.id)).where(Click.link_id == link.id))

    # total clicks per day of a given link
    day = func.date(Click.clicked_at)
    per_day = db.execute(
        select(day, func.count())
        .where(Click.link_id == link.id)
        .group_by(day)
        .order_by(day)
    ).all()

    # top 5 referrers (sources) of a given link 
    ref = func.coalesce(Click.referrer, "direct")
    top_refs = db.execute(
        select(ref, func.count())
        .where(Click.link_id == link.id)
        .group_by(ref)
        .order_by(func.count().desc())
        .limit(5)
    ).all()

    return {
        "code": link.code,
        "original_url": link.original_url,
        "total_clicks": total,
        "clicks_per_day": [{"day": d, "clicks": c} for d, c in per_day],
        "top_referrers": [{"referrer": r, "clicks": c} for r, c in top_refs],
    }