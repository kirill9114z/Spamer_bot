import sqlite3
from datetime import datetime, timedelta
from threading import Lock

DB_PATH = "telegram_project.db"
db_lock = Lock()


def update_user_account_session(user_id, account_session):
    print(f"[DEBUG] Обновление account_session для user_id={user_id}: {account_session}")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE users
    SET account_session = ?
    WHERE user_id = ?
    """, (account_session, user_id))
    conn.commit()
    conn.close()


def get_user_account_session(user_id):
    """Возвращает сессию аккаунта, связанную с пользователем."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT account_session
    FROM users
    WHERE user_id = ?
    """, (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        print(f"[DEBUG] Для пользователя {user_id} найден account_session: {result[0]}")
    else:
        print(f"[DEBUG] Для пользователя {user_id} account_session не найден в базе данных.")
    return result[0] if result else None


def execute_query(query, params=()):
    """Выполняет запрос к базе данных с использованием блокировки."""
    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
        finally:
            conn.close()

def get_connection():
    """Устанавливает соединение с базой данных."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn


def add_user(user_id, username, group_name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            return

        cursor.execute("""
        INSERT INTO users (user_id, username, group_name, status)
        VALUES (?, ?, ?, 'new')
        """, (user_id, username, group_name))
        conn.commit()
    except Exception as e:
        print(f"[ERROR] Ошибка при добавлении пользователя {username}: {e}")
    finally:
        conn.close()



def update_user_status(user_id, status, reply=None):
    print(f"[DEBUG] Обновление статуса для user_id={user_id}: {status}, reply={reply}")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE users
    SET status = ?, reply = ?
    WHERE user_id = ?
    """, (status, reply, user_id))
    conn.commit()
    conn.close()


def get_users_for_messaging(limit=150):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT user_id, username
            FROM users
            WHERE status = 'new'
            LIMIT ?
        """, (limit,))
        users = cursor.fetchall()
        print(f"[DEBUG] Найдено пользователей для рассылки: {users}")
        return users
    except Exception as e:
        print(f"[ERROR] Ошибка при выборке пользователей для рассылки: {e}")
        return []
    finally:
        conn.close()



def add_account(session, proxy, daily_limit=150):
    """Добавляет аккаунт в таблицу accounts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR IGNORE INTO accounts (session, proxy, daily_limit)
    VALUES (?, ?, ?)
    """, (session, proxy, daily_limit))
    conn.commit()
    conn.close()


def update_account_sent_today(session, count):
    """Обновляет количество отправленных сообщений для аккаунта."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE accounts
    SET sent_today = sent_today + ?
    WHERE session = ?
    """, (count, session))
    conn.commit()
    conn.close()


def initialize_database():
    """Создает таблицы для проекта, если они еще не существуют."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        status TEXT CHECK(status IN ('new', 'sent', 'replied')) DEFAULT 'new',
        group_name TEXT,
        reply TEXT,
        account_session TEXT  -- Добавляем столбец для хранения сессии аккаунта
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        account_id INTEGER PRIMARY KEY AUTOINCREMENT,
        session TEXT UNIQUE NOT NULL,
        proxy TEXT,
        daily_limit INTEGER DEFAULT 50,
        sent_today INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS groups (
        group_name TEXT PRIMARY KEY,
        last_updated DATETIME
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO settings (key, value) VALUES ('last_reset', '1970-01-01 00:00:00')
    """)

    conn.commit()
    conn.close()
    print("База данных успешно инициализирована.")


def reset_daily_sent():
    """
    Сбрасывает счетчик отправленных сообщений для всех аккаунтов,
    если с последнего сброса прошло 24 часа.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT value FROM settings WHERE key = 'last_reset'")
    last_reset = cursor.fetchone()[0]
    last_reset_time = datetime.strptime(last_reset, "%Y-%m-%d %H:%M:%S")

    now = datetime.now()
    if now - last_reset_time >= timedelta(days=1):
        cursor.execute("UPDATE accounts SET sent_today = 0")
        cursor.execute("UPDATE settings SET value = ? WHERE key = 'last_reset'", (now.strftime("%Y-%m-%d %H:%M:%S"),))
        conn.commit()
        print("Счетчики сообщений сброшены.")
    else:
        print("Счетчики сообщений еще не требуют сброса.")

    conn.close()



def add_group(group_name):
    """Добавляет группу в таблицу groups."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR IGNORE INTO groups (group_name, last_updated)
    VALUES (?, ?)
    """, (group_name, datetime.now()))
    conn.commit()
    conn.close()


def update_group_last_updated(group_name):
    """Обновляет дату последнего обновления группы."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE groups
    SET last_updated = ?
    WHERE group_name = ?
    """, (datetime.now(), group_name))
    conn.commit()
    conn.close()


def get_all_groups():
    """Получает список всех групп."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT group_name FROM groups")
    groups = cursor.fetchall()
    conn.close()
    return [group[0] for group in groups]


def add_column_if_not_exists():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]  # Получаем имена столбцов

    if 'account_session' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN account_session TEXT")
        print("[INFO] Добавлен столбец account_session в таблицу users")

    conn.commit()
    conn.close()
def debug_users():
    """Выводит данные всех пользователей из таблицы."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, account_session, status FROM users")
    users = cursor.fetchall()
    conn.close()
    print("[DEBUG] Содержимое таблицы users:")
    for user in users:
        print(f"  user_id: {user[0]}, username: {user[1]}, account_session: {user[2]}, status: {user[3]}")

def debug_users_changes():
    """Отслеживает изменения в таблице users."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, account_session, status FROM users")
    users = cursor.fetchall()
    conn.close()
    print("[DEBUG] Состояние таблицы users:")
    for user in users:
        print(f"  user_id: {user[0]}, username: {user[1]}, account_session: {user[2]}, status: {user[3]}")

def reset_user_status():
    """Сбрасывает статус всех пользователей на 'new'."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        UPDATE users
        SET status = 'new'
        """)
        conn.commit()
        print("[INFO] Все статусы пользователей обновлены на 'new'.")
    except Exception as e:
        print(f"[ERROR] Ошибка при обновлении статусов пользователей: {e}")
    finally:
        conn.close()


def clear_users():
    """Удаляет всех пользователей из таблицы users."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users")
        conn.commit()
        print("[INFO] Все пользователи удалены из таблицы users.")
    except Exception as e:
        print(f"[ERROR] Ошибка при удалении пользователей: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    initialize_database()
    get_users_for_messaging()
    debug_users()




