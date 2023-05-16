from sqlalchemy.orm import relationship

from .base import BaseModel, db


class Category(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False, index=True)

    sources = relationship('Source', back_populates='category', cascade='all, delete-orphan')


class Source(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False, index=True)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id', ondelete="CASCADE"))
    category = relationship('Category', foreign_keys=[category_id], back_populates='sources')

    feeds = relationship('Feed', back_populates='source', cascade='all, delete-orphan')
