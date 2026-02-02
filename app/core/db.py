from sqlmodel import create_engine, SQLModel
from app.core.settings import settings
from app.models.user import User 
from app.models.github_account import GithubAccount
from app.models.github_activity_day import GithubActivityDay

db_name = "postgres"

db_url = f"postgresql+psycopg://postgres:{settings.POSTGRES_PASSWORD}@localhost:15432/postgres"

engine = create_engine(db_url)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    print(f"tables created!")

