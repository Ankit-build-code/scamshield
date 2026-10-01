from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    XAI_API_KEY: str = ""
    XAI_MODEL: str = "llama-3.3-70b-versatile"
    XAI_BASE_URL: str = "https://api.groq.com/openai/v1"

    class Config:
        env_file = ".env"

settings = Settings()