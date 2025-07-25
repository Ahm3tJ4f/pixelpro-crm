import os
from dotenv import load_dotenv

load_dotenv()

# Database
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

# Environment
DOCKER_ENV = os.getenv("DOCKER_ENV", "false").lower() == "true"
DB_HOST = "postgres" if DOCKER_ENV else "localhost"
DB_PORT = 5432

# Database URL
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}" 
