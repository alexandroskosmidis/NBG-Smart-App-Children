from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    GEMINI_API_KEY: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    APP_ENV: str = "development"
    APP_PORT: int = 8000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings() # type: ignore