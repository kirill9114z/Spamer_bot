import time
import random
from proxy_manager import get_next_account
from gather_users import gather_users_from_group
from send_messages import start_sending_messages


def run_account(account):
    print(f"Запуск аккаунта {account['session_name']}...")
    group_name = "target_group"  

    with Client(account["session_name"], api_id=account["api_id"], api_hash=account["api_hash"],
                proxy=account["proxy"]) as client:
        gather_users_from_group(group_name)  
        start_sending_messages(client, group_name)
        print(f"Аккаунт {account['session_name']} завершил работу.")


def run_all_accounts():
    """
    Последовательный запуск всех аккаунтов с задержкой.
    """
    accounts = ACCOUNTS.copy()
    random.shuffle(accounts) 

    while True:
        for account in accounts:
            run_account(account)

            delay = random.randint(3600, 10800)  
            print(f"Следующий аккаунт будет запущен через {delay // 60} минут.")
            time.sleep(delay)

        random.shuffle(accounts)
        print("Все аккаунты завершили работу. Начинаем новый цикл.")
