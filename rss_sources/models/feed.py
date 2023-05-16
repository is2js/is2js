from sqlalchemy.orm import relationship

from .base import BaseModel, db


class Feed(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False, index=True)
    thumbnail_url = db.Column(db.Text, nullable=True)
    body = db.Column(db.Text, nullable=True)
    published = db.Column(db.DateTime(timezone=True))
    published_string = db.Column(db.Text, nullable=True)

    source_id = db.Column(db.Integer, db.ForeignKey('source.id', ondelete="CASCADE"))
    source = relationship('Source', foreign_keys=[source_id], back_populates='feeds')
