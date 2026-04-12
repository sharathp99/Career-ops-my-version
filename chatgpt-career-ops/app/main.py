from src.api import create_app
from src.infrastructure.db.base import Base
from src.infrastructure.db.session import engine
from src.infrastructure.db import models  # noqa: F401

Base.metadata.create_all(bind=engine)
app = create_app()
