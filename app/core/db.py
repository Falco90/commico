from sqlmodel import create_engine, SQLModel, Session
from app.core.settings import settings

db_name = "postgres"

db_url = f"postgresql+psycopg://postgres:{settings.POSTGRES_PASSWORD}@localhost:15432/postgres"

engine = create_engine(db_url)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    print(f"tables created!")

def get_session():
    with Session(engine) as session:
        yield session
