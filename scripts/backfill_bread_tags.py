"""Backfill script to create BreadTag rows and populate associations

Run this script with the project environment active. It will:
 - create `bread_tags` table if missing
 - create seed tags
 - associate existing bakeries that have `bread_tags` array values
"""
from app.config.database import engine, SessionLocal
from app.models import Base, Bakery, BreadTag


SEED_TAGS = [
    "크로아상",
    "식빵",
    "크림빵",
    "도넛",
    "마카롱",
    "바게트",
    "케이크",
    "파이",
    "베이글",
    "브리오슈",
    "라운드빵",
]


def ensure_tables():
    # Create tables for models that might be new
    Base.metadata.create_all(bind=engine, tables=[BreadTag.__table__])


def seed_tags(session):
    for name in SEED_TAGS:
        tag = session.query(BreadTag).filter(BreadTag.name == name).first()
        if not tag:
            tag = BreadTag(name=name, slug=name)
            session.add(tag)
    session.commit()


def backfill_associations(session):
    bakeries = session.query(Bakery).filter(Bakery.bread_tags != None).all()
    for bakery in bakeries:
        arr = bakery.bread_tags or []
        for tag_name in arr:
            tag_name = tag_name.strip()
            if not tag_name:
                continue
            tag = session.query(BreadTag).filter(BreadTag.name == tag_name).first()
            if tag and tag not in bakery.bread_tags_rel:
                bakery.bread_tags_rel.append(tag)
    session.commit()


if __name__ == "__main__":
    ensure_tables()
    session = SessionLocal()
    try:
        seed_tags(session)
        backfill_associations(session)
        print("Backfill complete")
    finally:
        session.close()
