from pymongo import MongoClient
from bson.objectid import ObjectId
from faker import Faker
import pprint
import random
import sys

# Ініціалізація Faker
faker = Faker("en_US")

# Спроба підключення до MongoDB з перевіркою
try:
    client = MongoClient("mongodb://localhost:27017/",
                         serverSelectionTimeoutMS=2000)
    client.server_info()
except Exception as e:
    print(f"Помилка підключення до MongoDB: {e}")
    sys.exit(1)

# Вибір бази та колекції
db = client["cat_database"]
collection = db["cats"]

FEATURE_POOL = [
    "любить рибу", "боїться пилососа", "ходить по клавіатурі",
    "муркоче голосно", "стрибає високо", "любить спати",
    "грається з клубком ниток", "шипить на гостей", "просить їжу",
    "лізе в коробки", "треться об ноги"
]


def print_all_cats():
    print("Всі коти у базі:")
    cats = list(collection.find())
    if not cats:
        print("📭 База порожня.")
        return
    for cat in cats:
        name = cat.get("name", "Невідомо")
        age = cat.get("age", "Невідомо")
        features = ", ".join(cat.get("features", []))
        print(f"🐈 Ім'я: {name} | Вік: {age} | Характеристики: {features}")


def find_cat_by_name():
    name = input("Введіть ім’я кота: ").strip()
    if not name:
        print("Ім’я не може бути порожнім.")
        return
    cat = collection.find_one(
        {"name": {"$regex": f"^{name}$", "$options": "i"}})
    if cat:
        pprint.pprint(cat)
    else:
        print("Кота з таким ім’ям не знайдено.")


def update_cat_age():
    name = input("Введіть ім’я кота для оновлення віку: ").strip()
    if not name:
        print("Ім’я не може бути порожнім.")
        return
    new_age = input("Введіть новий вік: ").strip()
    if not new_age.isdigit() or not (0 < int(new_age) < 50):
        print("Вік повинен бути числом від 1 до 49.")
        return
    result = collection.update_one(
        {"name": {"$regex": f"^{name}$", "$options": "i"}},
        {"$set": {"age": int(new_age)}}
    )
    if result.matched_count:
        print("Вік оновлено.")
    else:
        print("Кота не знайдено.")


def add_feature_to_cat():
    name = input(
        "Введіть ім’я кота для додавання нової характеристики: ").strip()
    if not name:
        print("Ім’я не може бути порожнім.")
        return
    new_feature = input("Введіть нову характеристику: ").strip()
    if not new_feature:
        print("Характеристика не може бути порожньою.")
        return
    result = collection.update_one(
        {"name": {"$regex": f"^{name}$", "$options": "i"}},
        {"$addToSet": {"features": new_feature}}
    )
    if result.matched_count:
        print("Характеристика додана.")
    else:
        print("Кота не знайдено.")


def delete_cat_by_name():
    name = input("Введіть ім’я кота для видалення: ").strip()
    if not name:
        print("Ім’я не може бути порожнім.")
        return
    result = collection.delete_one(
        {"name": {"$regex": f"^{name}$", "$options": "i"}})
    if result.deleted_count:
        print("Кота видалено.")
    else:
        print("Кота не знайдено.")


def delete_all_cats():
    confirm = input(
        "Ви впевнені, що хочете видалити всіх котів? (yes/no): ").strip()
    if confirm.lower() == 'yes':
        result = collection.delete_many({})
        print(f"Видалено {result.deleted_count} записів.")
    else:
        print("Операція скасована.")


def insert_sample_data():
    """Опціональна функція для вставки початкових даних"""
    sample = {
        "name": "Barsik",
        "age": 3,
        "features": ["ходить в капці", "дає себе гладити", "рудий"]
    }
    collection.insert_one(sample)
    print("Зразок додано.")


def generate_fake_cats():
    """Генерує випадкових котів та додає їх у базу"""
    try:
        count = int(input("Скільки випадкових котів згенерувати?: ").strip())
        if count <= 0:
            print("Кількість повинна бути більше нуля.")
            return
    except ValueError:
        print("Введіть правильне число.")
        return

    fake_cats = []
    for _ in range(count):
        cat = {
            "name": faker.first_name(),
            "age": random.randint(1, 20),
            "features": random.sample(FEATURE_POOL, k=random.randint(2, 4))
        }
        fake_cats.append(cat)

    result = collection.insert_many(fake_cats)
    print(f"Додано {len(result.inserted_ids)} випадкових котів.")


def main_menu():
    while True:
        print("\n===== 🐾 Меню 🐾 =====")
        print("1. Показати всіх котів")
        print("2. Знайти кота за ім’ям")
        print("3. Оновити вік кота")
        print("4. Додати характеристику коту")
        print("5. Видалити кота за ім’ям")
        print("6. Видалити всіх котів")
        print("7. Додати зразок")
        print("8. Згенерувати випадкових котів")
        print("0. Вийти")
        choice = input("Ваш вибір: ").strip()

        if choice == '1':
            print_all_cats()
        elif choice == '2':
            find_cat_by_name()
        elif choice == '3':
            update_cat_age()
        elif choice == '4':
            add_feature_to_cat()
        elif choice == '5':
            delete_cat_by_name()
        elif choice == '6':
            delete_all_cats()
        elif choice == '7':
            insert_sample_data()
        elif choice == '8':
            generate_fake_cats()
        elif choice == '0':
            print("До побачення!")
            break
        else:
            print("Невірний вибір. Спробуйте ще раз.")


if __name__ == "__main__":
    main_menu()
