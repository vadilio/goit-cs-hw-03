import logging
import db_conf
from db_conf import get_cursor

logging.basicConfig(
    level=logging.INFO,  # или DEBUG
    format='%(asctime)s %(levelname)s:%(message)s',
    handlers=[
        logging.FileHandler("task_manager.log", encoding='utf-8'),
        logging.StreamHandler()  # щоб також бачити вивід у консолі
    ]
)


def create_tab():
    conn, cur = get_cursor(db_conf.dbname, db_conf.user,
                           db_conf.password, db_conf.host, db_conf.port)
    if not conn or not cur:
        # logging.error(
        #     "Не вдалося отримати курсор. Перевірте параметри підключення.")
        return

    try:
        with open("create_tab.sql", "r", encoding="utf-8") as f:
            sql = f.read()

        with conn, cur:
            cur.execute(sql)
            conn.commit()
            logging.info(
                "Таблиці успішно пересоздані з файлу create_tab.sql.")
    except FileNotFoundError:
        logging.error("Файл create_tab.sql не знайдено.")
    except Exception as e:
        logging.error("Помилка під час виконання SQL: %s", e)
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    create_tab()
