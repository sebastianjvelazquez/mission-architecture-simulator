 
from functools import lru_cache
from typing import Optional
 
from pydantic_settings import BaseSettings
 
 
class Settings(BaseSettings):

    ENVIRONMENT: str = "development"
 
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/mission_simulator"
 
    # Comma-separated list of allowed origins.
    # The middleware helper merges this with FRONTEND_URL automatically.
    ALLOWED_ORIGINS: str = "http://localhost:3000"
 
    # Canonical Vercel frontend URL.  Set this on Render so you only have
    # to update one variable when the frontend URL changes.
    FRONTEND_URL: Optional[str] = None
    SECRET_KEY: str = "changeme-use-a-real-secret-in-production"
 
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Allow extra variables in .env without raising validation errors.
        extra = "ignore"
 
    def get_allowed_origins(self) -> list[str]:
        origins = [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]
 
        if self.FRONTEND_URL:
            frontend = self.FRONTEND_URL.rstrip("/")
            if frontend and frontend not in origins:
                origins.append(frontend)
 
        # Always allow localhost in development so devs don't get locked out.
        if self.ENVIRONMENT == "development" and "http://localhost:3000" not in origins:
            origins.append("http://localhost:3000")
 
        return origins
 
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"
 
 
@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (reads .env once at startup)."""
    return Settings()
