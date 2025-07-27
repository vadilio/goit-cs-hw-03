import os
import time
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from dotenv import load_dotenv

load_dotenv()

MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = int(os.getenv("MONGO_PORT"))
ROOT_USER = os.getenv("MONGO_ROOT_USER")
ROOT_PASS = os.getenv("MONGO_ROOT_PASS")

DB_NAME = os.getenv("CAT_DB")
CAT_USER = os.getenv("CAT_USER")
CAT_PASS = os.getenv("CAT_PASS")

# Підключення як root
uri_root = f"mongodb://{ROOT_USER}:{ROOT_PASS}@{MONGO_HOST}:{MONGO_PORT}/admin"

print("Підключення до MongoDB як root...")
client = None
for attempt in range(10):
    try:
        client = MongoClient(uri_root, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        print("Підключено.")
        break
    except Exception as e:
        print(f"Спроба {attempt + 1}: {e}")
        time.sleep(3)

if not client:
    print("Неможливо підключитися до MongoDB.")
    exit(1)

# Створення користувача
try:
    client[DB_NAME].command("createUser", CAT_USER, pwd=CAT_PASS, roles=[
        {"role": "readWrite", "db": DB_NAME}
    ])
    print("Користувача створено.")
except OperationFailure as e:
    if "already exists" in str(e):
        print("ℹКористувач вже існує.")
    else:
        print("Помилка при створенні користувача:", e)
        exit(1)

# Перепідключення як новий користувач
print("🔁 Підключення як новий користувач...")
uri_user = f"mongodb://{CAT_USER}:{CAT_PASS}@{MONGO_HOST}:{MONGO_PORT}/{DB_NAME}"
user_client = MongoClient(uri_user, serverSelectionTimeoutMS=3000)
db = user_client[DB_NAME]

# Додавання записів
try:
    db.cats.insert_many([
        {"name": "barsik", "age": 3, "features": [
            "ходить в капці", "дає себе гладити", "рудий"]},
        {"name": "murzik", "age": 2, "features": [
            "грається з мишкою", "бігає по хаті"]}
    ])
    print("Коти додані.")
except Exception as e:
    print("Помилка при додаванні котів:", e)

user_client.close()
