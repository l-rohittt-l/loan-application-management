"""
The database connection.

Three things live here, and the tests import two of them by name:
  - `Base`: the parent class every table model inherits from
  - `get_db`: hands a database session to each request, then closes it
  - `init_db`: creates the tables on first start
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# `check_same_thread=False` is required for SQLite when a web server handles
# several requests at once. Without it SQLite refuses connections from any
# thread other than the one that opened the file.
#
# We deliberately do NOT turn on SQLite's foreign-key checking. Two of the
# trainer's tests insert rows that point at an applicant who does not exist,
# and would fail if SQLite enforced the link. See TRAPS-AND-DECISIONS T-03.
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

# A "session" is one conversation with the database. Each request gets its own.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Every model class inherits from this so SQLAlchemy knows it is a table.
Base = declarative_base()


def get_db():
    """
    Give the request a session, and always close it afterwards, even if the
    request failed. FastAPI calls this for every endpoint that asks for a db.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create any tables that do not exist yet. Safe to call every startup."""
    # Importing the models package registers every table with Base.
    from app import models  # noqa: F401  (imported for its side effect)

    Base.metadata.create_all(bind=engine)
