from faker import Faker
import random
import db_conf
from db_conf import get_cursor
import logging

logging.basicConfig(
    level=logging.INFO,  # или DEBUG
    format='%(asctime)s %(levelname)s:%(message)s',
    handlers=[
        logging.FileHandler("task_manager.log", encoding='utf-8'),
        logging.StreamHandler()  # чтобы видеть вывод в консоли тоже
    ]
)


def seed_data(num_users=10, num_tasks=30):
    fake = Faker()
    conn, cur = get_cursor(db_conf.dbname, db_conf.user,
                           db_conf.password, db_conf.host, db_conf.port)
    if not conn or not cur:
        logging.error(
            "Не вдалося отримати курсор. Перевірте параметри підключення.")
        return

    try:
        with conn, cur:
            statuses = ['new', 'in progress', 'completed']
            insert_status_sql = "INSERT INTO status (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;"
            for status in statuses:
                cur.execute(insert_status_sql, (status,))

            user_ids = []
            insert_user_sql = "INSERT INTO users (fullname, email) VALUES (%s, %s) RETURNING id;"
            for _ in range(num_users):
                fullname = fake.name()
                email = fake.unique.email()
                cur.execute(insert_user_sql, (fullname, email))
                user_id = cur.fetchone()[0]
                user_ids.append(user_id)

            cur.execute("SELECT id FROM status;")
            status_ids = [row[0] for row in cur.fetchall()]

            insert_task_sql = """
            INSERT INTO tasks (title, description, status_id, user_id)
            VALUES (%s, %s, %s, %s);
            """
            for _ in range(num_tasks):
                title = fake.sentence(nb_words=6)
                description = fake.text(max_nb_chars=200)
                status_id = random.choice(status_ids)
                user_id = random.choice(user_ids)
                cur.execute(insert_task_sql,
                            (title, description, status_id, user_id))

        logging.info("Таблиці успішно заповнені.")
    except Exception as e:
        logging.error("Помилка при заповненні таблиць: %s", e)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
