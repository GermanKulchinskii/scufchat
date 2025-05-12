from sqlmodel import Session, SQLModel, create_engine

from fapigraphproject.config import Config

engine = create_engine(Config.DATABASE_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
