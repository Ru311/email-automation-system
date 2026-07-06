from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load variables from .env into the environment (safe no-op if .env is absent).
load_dotenv()


DATABASE_URL = os.environ.get("DATABASE_URL", "")

engine = create_engine(
    DATABASE_URL,
    pool_size=2,
    max_overflow=0,
    pool_pre_ping=True
)