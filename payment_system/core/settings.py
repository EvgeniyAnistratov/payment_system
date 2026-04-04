from python_utils.settings import read_variable, ConfigVarType

APP_TITLE = "Payment system"

DB_NAME: str = read_variable("DB_NAME")
DB_USER: str = read_variable("DB_USER")
DB_PASSWORD: str = read_variable("DB_PASSWORD")
DB_HOST: str = read_variable("DB_HOST")
DB_PORT: int = read_variable("DB_PORT", ConfigVarType.INT, default=5432, required=False)
