from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base


# Association table between bakeries and bread_tags
bakery_bread_tag = Table(
    "bakery_bread_tag",
    Base.metadata,
    Column("bakery_id", String, ForeignKey("bakeries.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("bread_tags.id"), primary_key=True),
)


class BreadTag(Base):
    __tablename__ = "bread_tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False, unique=True, index=True)  # e.g. '크로아상'
    slug = Column(String(128), nullable=True, unique=True, index=True)  # e.g. 'croissant'

    # Relationship back to bakeries
    bakeries = relationship("Bakery", secondary=bakery_bread_tag, back_populates="bread_tags_rel")

    def __repr__(self):
        return f"<BreadTag(id={self.id}, name={self.name})>"
