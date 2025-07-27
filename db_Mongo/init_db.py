import os
import time
from pymongo import MongoClient
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError, DuplicateKeyError, BulkWriteError
from dotenv import load_dotenv

load_dotenv()

MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
ROOT_USER = os.getenv("MONGO_ROOT_USER")
ROOT_PASS = os.getenv("MONGO_ROOT_PASS")

DB_NAME = os.getenv("CAT_DB", "cat_db")
CAT_USER = os.getenv("CAT_USER")
CAT_PASS = os.getenv("CAT_PASS")
CAT_COLLECTION = os.getenv("CAT_COLLECTION", "cats")


def initdb():
    uri_root = f"mongodb://{ROOT_USER}:{ROOT_PASS}@{MONGO_HOST}:{MONGO_PORT}/admin"

    # ===== Підключення як root =====
    print("Підключення до MongoDB як root...")
    client = None
    for attempt in range(3):
        try:
            client = MongoClient(uri_root, serverSelectionTimeoutMS=3000)
            client.admin.command("ping")
            print("Підключення встановлено.")
            break
        except ServerSelectionTimeoutError as e:
            print(f"Спроба {attempt + 1}: {e}")
            time.sleep(3)

    if not client:
        print("Неможливо підключитися до MongoDB як root.")
        exit(1)

    # ===== Створення користувача =====
    try:
        client[DB_NAME].command("createUser", CAT_USER, pwd=CAT_PASS, roles=[
            {"role": "readWrite", "db": DB_NAME}
        ])
        print("Користувач створений.")
    except OperationFailure as e:
        if "already exists" in str(e):
            print("Користувач вже існує.")
        else:
            print(f"Помилка при створенні користувача: {e}")
            exit(1)

    # ===== Перепідключення як звичайний користувач =====
    print("Перепідключення як користувач...")
    uri_user = f"mongodb://{CAT_USER}:{CAT_PASS}@{MONGO_HOST}:{MONGO_PORT}/{DB_NAME}"

    try:
        user_client = MongoClient(uri_user, serverSelectionTimeoutMS=3000)
        user_client[DB_NAME].command("ping")
        print("Авторизація користувача успішна.")
    except Exception as e:
        print(f"Помилка при підключенні як користувач: {e}")
        exit(1)

    # ===== Додавання котів =====
    db = user_client[DB_NAME]
    cats_collection = db[CAT_COLLECTION]

    # Перевірка та створення унікального індексу за полем "name"
    try:
        existing_indexes = cats_collection.index_information()
        if "name_1" not in existing_indexes:
            cats_collection.create_index("name", unique=True)
            print("Унікальний індекс за іменем кота створено.")
        else:
            print("Унікальний індекс уже існує.")
    except Exception as e:
        print(f"Помилка при створенні індексу: {e}")

    # Додаємо котів
    try:
        result = cats_collection.insert_many([
            {
                "name": "barsik",
                "age": 3,
                "features": ["ходит в капці", "дає себе гладити", "рудий"]
            },
            {
                "name": "murzik",
                "age": 2,
                "features": ["грається з мишкою", "бігає по хаті"]
            }
        ], ordered=False)
        print(f"Коти додані: {len(result.inserted_ids)} записів.")
    except BulkWriteError as bwe:
        print("Помилка: один або кілька котів вже існують.")
        for error in bwe.details.get("writeErrors", []):
            print(f" - {error.get('errmsg')}")
    except Exception as e:
        print(f"Несподівана помилка при додаванні котів: {e}")

    # ===== Завершение =====
    user_client.close()
    client.close()
    print("З’єднання закриті.")


if __name__ == "__main__":
    initdb()
