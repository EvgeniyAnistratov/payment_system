from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DbSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_", env_file=".env", extra="ignore")

    host: str
    port: int = 5432
    name: str
    user: str
    password: SecretStr
    logging: bool = False

    @property
    def async_url(self) -> str:
        password = self.password.get_secret_value()
        return f"postgresql+asyncpg://{self.user}:{password}@{self.host}:{self.port}/{self.name}"

    @property
    def sync_url(self) -> str:
        password = self.password.get_secret_value()
        return f"postgresql+psycopg2://{self.user}:{password}@{self.host}:{self.port}/{self.name}"


class JwtSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="JWT_", env_file=".env", extra="ignore")

    secret_key: SecretStr
    algorithm: str = "HS256"
    access_ttl: int = 30


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="ignore")

    port: int = 8000
    transaction_secret: SecretStr
    title: str = "Payment system"
