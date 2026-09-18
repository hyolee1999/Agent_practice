from sqlmodel import Field, SQLModel, create_engine, Session
from docuagent.config.settings import settings

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: str
    hashed_password: str


engine = create_engine(settings.database_url)


def create_db_and_tables():
    """Create database and tables."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Get a database session."""
    with Session(engine) as session:
        yield session


