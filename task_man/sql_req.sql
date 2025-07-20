-- 1. Отримати всі завдання певного користувача
SELECT * FROM tasks WHERE user_id = 1;

-- 2. Вибрати завдання за певним статусом ('new')
SELECT * FROM tasks WHERE status_id = (SELECT id FROM status WHERE name = 'new');

-- 3. Оновити статус конкретного завдання
UPDATE tasks SET status_id = (SELECT id FROM status WHERE name = 'in progress') WHERE id = 5;

-- 4. Користувачі без жодного завдання
SELECT * FROM users WHERE id NOT IN (SELECT DISTINCT user_id FROM tasks);

-- 5. Додати нове завдання для користувача
INSERT INTO tasks (title, description, status_id, user_id)
VALUES ('New Task', 'Description here', (SELECT id FROM status WHERE name = 'new'), 1);

-- 6. Завдання, які ще не завершені
SELECT * FROM tasks WHERE status_id != (SELECT id FROM status WHERE name = 'completed');

-- 7. Видалити конкретне завдання
DELETE FROM tasks WHERE id = 10;

-- 8. Знайти користувачів з певною поштою
SELECT * FROM users WHERE email LIKE '%@gmail.com';

-- 9. Оновити ім’я користувача
UPDATE users SET fullname = 'Новий Ім’я' WHERE id = 3;

-- 10. Кількість завдань для кожного статусу
SELECT s.name, COUNT(t.id) AS task_count
FROM status s
LEFT JOIN tasks t ON s.id = t.status_id
GROUP BY s.name;

-- 11. Завдання користувачів з певним доменом пошти
SELECT t.*
FROM tasks t
JOIN users u ON t.user_id = u.id
WHERE u.email LIKE '%@example.com';

-- 12. Завдання без опису
SELECT * FROM tasks WHERE description IS NULL;

-- 13. Користувачі та їхні завдання у статусі 'in progress'
SELECT u.fullname, t.title
FROM users u
JOIN tasks t ON u.id = t.user_id
WHERE t.status_id = (SELECT id FROM status WHERE name = 'in progress');

-- 14. Кількість завдань для кожного користувача
SELECT u.fullname, COUNT(t.id) AS task_count
FROM users u
LEFT JOIN tasks t ON u.id = t.user_id
GROUP BY u.fullname;