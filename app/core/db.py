from sqlmodel import create_engine
from settings import settings

db_name = "postgres"

db_url = f"postgresql+psycopg://postgres:{settings.POSTGRES_PASSWORD}@localhost:15432/postgres"

engine = create_engine(db_url)
