import logging
from psycopg2 import sql

logging.basicConfig(
    level=logging.INFO,  # или DEBUG
    format='%(asctime)s %(levelname)s:%(message)s',
    handlers=[
        logging.FileHandler("task_manager.log", encoding='utf-8'),
        logging.StreamHandler()  # чтобы видеть вывод в консоли тоже
    ]
)


def print_results(description, rows):
    logging.info(f"\n{description}:")
    for row in rows:
        print(row)
        # logging.info(row)


def get_user_ids(cur):
    cur.execute("SELECT id FROM users ORDER BY id")
    return [row[0] for row in cur.fetchall()]


def select_tasks_by_user(cur, user_id):
    cur.execute("SELECT * FROM tasks WHERE user_id = %s", (user_id,))
    print_results(f"Задачи пользователя id={user_id}", cur.fetchall())


def select_tasks_by_status(cur, status_name):
    cur.execute("""
        SELECT * FROM tasks 
        WHERE status_id = (SELECT id FROM status WHERE name = %s)
    """, (status_name,))
    print_results(f"Задачи со статусом '{status_name}'", cur.fetchall())


def update_task_status(cur, task_id, new_status):
    cur.execute("""
        UPDATE tasks 
        SET status_id = (SELECT id FROM status WHERE name = %s)
        WHERE id = %s
    """, (new_status, task_id))
    logging.info(f"Статус задачи id={task_id} обновлен на '{new_status}'.")


def insert_task(cur, title, description, status_name, user_id):
    cur.execute("""
        INSERT INTO tasks (title, description, status_id, user_id)
        VALUES (%s, %s, 
            (SELECT id FROM status WHERE name = %s), 
            %s)
    """, (title, description, status_name, user_id))
    logging.info(f"Добавлена задача '{title}' для пользователя id={user_id}.")


def delete_task_by_id(cur, task_id):
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    logging.info(f"Задача id={task_id} удалена.")


def delete_last_task(cur):
    cur.execute("SELECT id FROM tasks ORDER BY id DESC LIMIT 1")
    result = cur.fetchone()
    if result:
        delete_task_by_id(cur, result[0])
        logging.info(f"Задача удалена.")


def users_without_tasks(cur):
    cur.execute("""
        SELECT * FROM users 
        WHERE id NOT IN (SELECT DISTINCT user_id FROM tasks)
    """)
    print_results("Користувачі без завдань", cur.fetchall())


def tasks_not_completed(cur):
    cur.execute("""
        SELECT * FROM tasks 
        WHERE status_id != (SELECT id FROM status WHERE name = 'completed')
    """)
    print_results("Завдання, що не завершені", cur.fetchall())


def search_users_by_email_domain(cur, domain):
    cur.execute(sql.SQL("SELECT * FROM users WHERE email LIKE %s"),
                (f"%@{domain}",))
    print_results(f"Користувачі з email '@{domain}'", cur.fetchall())


def update_user_fullname(cur, user_id, new_name):
    cur.execute("UPDATE users SET fullname = %s WHERE id = %s",
                (new_name, user_id))
    logging.info(f"Ім’я користувача id={user_id} оновлено на '{new_name}'.")


def summary_tasks_by_status(cur):
    cur.execute("""
        SELECT status.name, COUNT(tasks.id) 
        FROM status
        LEFT JOIN tasks ON status.id = tasks.status_id
        GROUP BY status.name
    """)
    print_results("Кількість завдань за статусами", cur.fetchall())


def tasks_by_user_email_domain(cur, domain):
    cur.execute("""
        SELECT tasks.*
        FROM tasks
        JOIN users ON tasks.user_id = users.id
        WHERE users.email LIKE %s
    """, (f"%@{domain}",))
    print_results(f"Завдання користувачів з email '@{domain}'", cur.fetchall())


def tasks_without_description(cur):
    cur.execute(
        "SELECT * FROM tasks WHERE description IS NULL OR description = ''")
    print_results("Завдання без опису", cur.fetchall())


def tasks_in_progress_with_users(cur):
    cur.execute("""
        SELECT users.fullname, tasks.title, status.name
        FROM tasks
        JOIN users ON tasks.user_id = users.id
        JOIN status ON tasks.status_id = status.id
        WHERE status.name = 'in progress'
    """)
    print_results(
        "Користувачі та їх завдання зі статусом 'in progress'", cur.fetchall())


def user_task_counts(cur):
    cur.execute("""
        SELECT users.fullname, COUNT(tasks.id)
        FROM users
        LEFT JOIN tasks ON users.id = tasks.user_id
        GROUP BY users.fullname
    """)
    print_results("Користувачі та кількість їх завдань", cur.fetchall())
