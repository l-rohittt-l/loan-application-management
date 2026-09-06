"""
Settings for the app, read from the .env file.

Every other file that needs a setting imports `settings` from here instead of
reading environment variables itself. That way there is one place to see what
the app can be configured with, and .env.example stays accurate.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Where to find the .env file, relative to where the server is started
    # (which is always the backend/ folder).
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ---- Application ----
    app_name: str = "loan-application-management"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    # Keep a copy of the log on disk, so a reference number can still be looked
    # up tomorrow. Off during tests, where it would only make noise.
    log_to_file: bool = True
    log_dir: str = "logs"

    # ---- Program identity, goes into every log line ----
    poc_id: str = "POC-01"
    phase: int = 1
    associate_id: str = "unknown"

    # ---- Database ----
    database_url: str = "sqlite:///./loan_app.db"

    # ---- Security ----
    secret_key: str = "change-me"          # .env overrides this with a real one
    access_token_expire_hours: int = 24
    jwt_algorithm: str = "HS256"

    # ---- Front-end ----
    # Comma-separated list of origins allowed to call the API from a browser.
    cors_origins: str = "http://localhost:5173"

    # ---- OpenTelemetry ----
    otel_service_name: str = "poc-01-phase-1"
    # "console" prints every span to the terminal; "none" switches spans off (tests).
    otel_exporter: str = "console"

    @property
    def cors_origin_list(self) -> list[str]:
        """The CORS setting as a Python list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
