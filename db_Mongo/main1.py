from pymongo import MongoClient
from pymongo.errors import OperationFailure
from bson.objectid import ObjectId
from faker import Faker
import pprint
import random
import sys

faker = Faker("en_US")

# Подключение к MongoDB с базовой проверкой соединения
try:
    client = MongoClient("mongodb://localhost:27017/",
                         serverSelectionTimeoutMS=2000)
    client.server_info()
except Exception as e:
    print(f"Ошибка подключения к MongoDB: {e}")
    sys.exit(1)

db = client["cat_database"]
collection = db["cats"]

FEATURE_POOL = [
    "likes fish", "fears vacuum", "walks on keyboard",
    "purrs loudly", "jumps high", "sleeps often",
    "plays with yarn", "hisses at guests", "begs for food",
    "crawls into boxes", "rubs against legs"
]


def safe_run(func):
    """Обертка для перехвата ошибок авторизации MongoDB"""
    try:
        func()
    except OperationFailure as e:
        print(f"Ошибка авторизации: {e}")


def print_all_cats():
    print("All cats in the database:")
    cats = list(collection.find())
    if not cats:
        print("The database is empty.")
        return
    for cat in cats:
        name = cat.get("name", "Unknown")
        age = cat.get("age", "Unknown")
        features = ", ".join(cat.get("features", []))
        print(f"Name: {name} | Age: {age} | Features: {features}")


def find_cat_by_name():
    name = input("Enter cat's name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    cat = collection.find_one(
        {"name": {"$regex": f"^{name}$", "$options": "i"}})
    if cat:
        pprint.pprint(cat)
    else:
        print("No cat found with that name.")


def update_cat_age():
    name = input("Enter the name of the cat to update age: ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    new_age = input("Enter new age: ").strip()
    if not new_age.isdigit() or not (0 < int(new_age) < 50):
        print("Age must be a number between 1 and 49.")
        return
    result = collection.update_one(
        {"name": {"$regex": f"^{name}$", "$options": "i"}},
        {"$set": {"age": int(new_age)}}
    )
    if result.matched_count:
        print("Age updated.")
    else:
        print("No cat found.")


def add_feature_to_cat():
    name = input("Enter the name of the cat to add feature: ").strip()
    if not name:
        print("⚠️ Name cannot be empty.")
        return
    new_feature = input("Enter new feature: ").strip()
    if not new_feature:
        print("⚠️ Feature cannot be empty.")
        return
    result = collection.update_one(
        {"name": {"$regex": f"^{name}$", "$options": "i"}},
        {"$addToSet": {"features": new_feature}}
    )
    if result.matched_count:
        print("✅ Feature added.")
    else:
        print("😿 No cat found.")


def delete_cat_by_name():
    name = input("Enter the name of the cat to delete: ").strip()
    if not name:
        print("⚠️ Name cannot be empty.")
        return
    result = collection.delete_one(
        {"name": {"$regex": f"^{name}$", "$options": "i"}})
    if result.deleted_count:
        print("🗑️ Cat deleted.")
    else:
        print("😿 No cat found.")


def delete_all_cats():
    confirm = input(
        "Are you sure you want to delete all cats? (yes/no): ").strip()
    if confirm.lower() == 'yes':
        result = collection.delete_many({})
        print(f"🗑️ Deleted {result.deleted_count} cats.")
    else:
        print("Operation canceled.")


def insert_sample_data():
    sample = {
        "name": "Barsik",
        "age": 3,
        "features": ["walks in slippers", "lets you pet", "ginger"]
    }
    collection.insert_one(sample)
    print("📥 Sample cat added.")


def generate_fake_cats():
    try:
        count = int(input("How many random cats to generate?: ").strip())
        if count <= 0:
            print("⚠️ Number must be greater than zero.")
            return
    except ValueError:
        print("⚠️ Please enter a valid number.")
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
    print(f"✅ {len(result.inserted_ids)} fake cats added.")


def main_menu():
    while True:
        print("\n===== 🐾 Menu 🐾 =====")
        print("1. Show all cats")
        print("2. Find cat by name")
        print("3. Update cat's age")
        print("4. Add feature to cat")
        print("5. Delete cat by name")
        print("6. Delete all cats")
        print("7. Add sample cat")
        print("8. Generate random cats")
        print("0. Exit")
        choice = input("Your choice: ").strip()

        if choice == '1':
            safe_run(print_all_cats)
        elif choice == '2':
            safe_run(find_cat_by_name)
        elif choice == '3':
            safe_run(update_cat_age)
        elif choice == '4':
            safe_run(add_feature_to_cat)
        elif choice == '5':
            safe_run(delete_cat_by_name)
        elif choice == '6':
            safe_run(delete_all_cats)
        elif choice == '7':
            safe_run(insert_sample_data)
        elif choice == '8':
            safe_run(generate_fake_cats)
        elif choice == '0':
            print("👋 Goodbye!")
            break
        else:
            print("⚠️ Invalid choice. Try again.")


if __name__ == "__main__":
    main_menu()
