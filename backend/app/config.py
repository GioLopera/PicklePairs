from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str = "dev-secret-key"
    environment: str = "development"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def database_url_fixed(self) -> str:
        # Railway provides postgresql:// but SQLAlchemy 2.0 requires postgresql+psycopg2://
        url = self.database_url
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url

    class Config:
        env_file = ".env"


settings = Settings()
