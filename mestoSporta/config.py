from dotenv import dotenv_values

config = {**dotenv_values()}

DB = {
    "DB_NAME": "telegram_proj",
    "DB_USERNAME": "telegram_proj",
    "DB_PASSWORD": "telegram_proj",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
}
