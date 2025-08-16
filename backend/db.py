from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from backend.config import Settings

settings = Settings()

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    from backend import models  # noqa
    Base.metadata.create_all(bind=engine)
