import psycopg2
import logging

dbname = 'task_manager_db'
user = 'dbuser1'
password = 'userpass_1'
host = 'localhost'
port = '5432'

logging.basicConfig(
    level=logging.INFO,  # или DEBUG
    format='%(asctime)s %(levelname)s:%(message)s',
    handlers=[
        logging.FileHandler("task_manager.log", encoding='utf-8'),
        logging.StreamHandler()  # чтобы видеть вывод в консоли тоже
    ]
)


def get_cursor(dbn, usr, passwd, hst, prt):
    try:
        conn = psycopg2.connect(
            dbname=dbn,
            user=usr,
            password=passwd,
            host=hst,
            port=prt
        )
        cursor = conn.cursor()
        return conn, cursor
    except psycopg2.Error as e:
        logging.error(
            f"Помилка підключення до бази даних: {e}", exc_info=False)
        return None, None
