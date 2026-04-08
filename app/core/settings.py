from python_utils.settings import read_variable, ConfigVarType

# APP SETTINGS
APP_TITLE = "Payment system"
APP_TRANSACTION_SECRET: str = read_variable("APP_TRANSACTION_SECRET")

# JWT SETTINGS
JWT_ACCESS_TTL: int = read_variable(
    "JWT_ACCESS_TTL",
    ConfigVarType.INT,
    default=30,
    required=False
)
JWT_ALGORITHM: str = read_variable("JWT_ALGORITHM", default="HS256", required=False)
JWT_SECRET_KEY: str = read_variable("JWT_SECRET_KEY")
JWT_TOKEN_URL: str = "/api/auth/token"

# DB SETTINGS
DB_NAME: str = read_variable("DB_NAME")
DB_USER: str = read_variable("DB_USER")
DB_PASSWORD: str = read_variable("DB_PASSWORD")
DB_HOST: str = read_variable("DB_HOST")
DB_PORT: int = read_variable("DB_PORT", ConfigVarType.INT, default=5432, required=False)
DB_LOGGING: bool = read_variable("DB_LOGGING", ConfigVarType.BOOL, default=False, required=False)


def get_db_url() -> str:
    return f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def get_alembic_url() -> str:
    return f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
