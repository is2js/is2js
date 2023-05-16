from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from rss_sources import SourceConfig

# sqlite migrate 오류시 발생할 수 있는 버그 픽스
naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

Base = declarative_base()
Base.metadata = MetaData(naming_convention=naming_convention)

engine = create_engine(SourceConfig.DATABASE_URL, **SourceConfig.SQLALCHEMY_POOL_OPTIONS)
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base.query = session.query_property()