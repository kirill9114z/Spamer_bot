import time
import random
from proxy_manager import get_next_account
from gather_users import gather_users_from_group
from send_messages import start_sending_messages


def run_account(account):
    """
    Выполняет работу для одного аккаунта: сбор участников и отправка сообщений.
    """
    print(f"Запуск аккаунта {account['session_name']}...")
    group_name = "target_group"  # Укажите группу для сбора участников

    # Подключаемся через аккаунт
    with Client(account["session_name"], api_id=account["api_id"], api_hash=account["api_hash"],
                proxy=account["proxy"]) as client:
        gather_users_from_group(group_name)  # Сбор участников группы
        start_sending_messages(client, group_name)  # Отправка сообщений
        print(f"Аккаунт {account['session_name']} завершил работу.")


def run_all_accounts():
    """
    Последовательный запуск всех аккаунтов с задержкой.
    """
    accounts = ACCOUNTS.copy()
    random.shuffle(accounts)  # Тасуем список аккаунтов

    while True:
        for account in accounts:
            run_account(account)

            # Рандомная задержка перед запуском следующего аккаунта
            delay = random.randint(3600, 10800)  # От 1 до 3 часов
            print(f"Следующий аккаунт будет запущен через {delay // 60} минут.")
            time.sleep(delay)

        # Тасуем аккаунты перед новым циклом
        random.shuffle(accounts)
        print("Все аккаунты завершили работу. Начинаем новый цикл.")
