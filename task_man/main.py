import logging
from db_conf import dbname, user, password, host, port
from db_conf import get_cursor
from db_seed import seed_data
import db_queries as queries
from create_tabs import create_tab  # функция создания таблиц


logging.basicConfig(
    level=logging.INFO,  # или DEBUG
    format='%(asctime)s %(levelname)s:%(message)s',
    handlers=[
        logging.FileHandler("task_manager.log", encoding='utf-8'),
        logging.StreamHandler()  # чтобы видеть вывод в консоли тоже
    ]
)


def main():
    create_tab()
    seed_data(num_users=20, num_tasks=30)

    conn, _ = get_cursor(dbname, user,
                         password, host, port)
    if not conn:
        return
    with conn.cursor() as cur:
        user_ids = queries.get_user_ids(cur)
        if len(user_ids) < 2:
            logging.warning("Недостатньо користувачів для демонстрації.")
            return

        queries.select_tasks_by_user(cur, user_ids[0])
        queries.select_tasks_by_status(cur, 'new')
        queries.update_task_status(
            cur, task_id=1, new_status='in progress')
        queries.insert_task(cur, "Нове завдання",
                            "Опис", "new", user_ids[1])
        queries.tasks_not_completed(cur)
        queries.users_without_tasks(cur)
        queries.delete_last_task(cur)
        queries.search_users_by_email_domain(cur, "example.com")
        queries.update_user_fullname(cur, user_ids[0], "Иван Иванович")
        queries.summary_tasks_by_status(cur)
        queries.tasks_by_user_email_domain(cur, "example.com")
        queries.tasks_without_description(cur)
        queries.tasks_in_progress_with_users(cur)
        queries.user_task_counts(cur)

    conn.commit()


if __name__ == "__main__":
    main()
