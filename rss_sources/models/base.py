from datetime import datetime
from functools import wraps

from sqlalchemy.orm import declared_attr

from rss_sources.database.base import session, Base
import sqlalchemy as db

from rss_sources.utils import db_logger


def transaction(f):
    """ Decorator for database (session) transactions."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            value = f(*args, **kwargs)

            session.commit()
            return value
        except Exception as e:
            session.rollback()
            # raise
            db_logger.error(f'{str(e)}')

    return wrapper


class BaseModel(Base):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    created_at = db.Column(db.DateTime(timezone=True), nullable=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_or_create(cls, get_key=None, **kwargs):
        if not get_key:
            instance = cls.query.filter_by(**kwargs).first()
        else:
            instance = cls.query.filter(getattr(cls, get_key) == kwargs.get(get_key)).first()
        if instance is None:
            instance = cls(**kwargs)
            instance.save()

        return instance

    @classmethod
    @transaction
    def get_list(cls):
        items = cls.query.all()
        return items

    @transaction
    def save(self):
        session.add(self)
        return self

    @transaction
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    @transaction
    def delete(self):
        session.delete(self)
        return self

    def to_dict(self):
        data = dict()

        for col in self.__table__.columns:
            _key = col.name
            _value = getattr(self, _key)
            data[_key] = _value

        return data
