import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME = "FINKO AI Backend"
    APP_VERSION = "1.0.0"

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    OPENAI_VECTOR_STORE_ID = os.getenv("OPENAI_VECTOR_STORE_ID", "")
    API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN", "")
    DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/finko.sqlite3")

settings = Settings()