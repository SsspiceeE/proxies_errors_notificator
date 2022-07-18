from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str('BOT_TOKEN')
CHAT_ID = env.int('CHAT_ID')
SQLALCHEMY_DATABASE_URL = env.str('SQLALCHEMY_DATABASE_URL')
CREDENTIALS_FILE = env.str('CREDENTIALS_FILE')
SPREADSHEET_ID = env.str('SPREADSHEET_ID')
