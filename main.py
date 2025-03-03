import random
import asyncio
from pyrogram import Client
from proxy_manager import ACCOUNTS
from gather_users import gather_users_from_group
from send_messages import start_sending_messages
from handle_replies import monitor_replies_for_account
from database import reset_daily_sent
import os

DAILY_MESSAGE_LIMIT = random.randint(30,50)
DELAY_BETWEEN_ACCOUNTS = (1800, 3600)

clients = {}


def delete_sessions():
    for account in ACCOUNTS:
        session_file = f"{account['session_name']}.session"
        if os.path.exists(session_file):
            os.remove(session_file)
            print(f"[INFO] Удален файл сессии: {session_file}")


async def initialize_client(account):
    session_name = account["session_name"]
    try:
        client = Client(
            name=session_name,
            api_id=account['api_id'],
            api_hash=account['api_hash']
        )
        await client.start()
        clients[session_name] = client
        print(f"[INFO] Клиент {session_name} успешно запущен.")
        return client
    except Exception as e:
        print(f"[ERROR] Ошибка при создании клиента для {session_name}: {e}")
        return None





async def run_account_workflow(client, account):
    """Рабочий процесс: рассылка сообщений и запуск мониторинга."""
    if client is None:
        print(f"[ERROR] Клиент для {account['session_name']} не был создан.")
        return

    try:
        print(f"[INFO] Аккаунт {account['session_name']} начал работу.")

        # Запускаем мониторинг сообщений как фоновую задачу
        asyncio.create_task(monitor_replies_for_account(client, clients))

        grupp = ['stokvostok']
        for i in grupp:
            print("[DEBUG] Начинаем сбор участников...")
            await gather_users_from_group(client=client, group_name=i, account=account)
            print("[DEBUG] Завершен сбор участников.")

            success = await start_sending_messages(client, group_name=i, account=account)
            if not success:
                break

            print(f"[INFO] Аккаунт {account['session_name']} завершил рассылку.")
    except Exception as e:
        print(f"[ERROR] Ошибка при работе с аккаунтом {account['session_name']}: {e}")
    finally:
        print(f"[INFO] Мониторинг аккаунта {account['session_name']} продолжает работу.")

def debug_clients():
    print("[DEBUG] Состояние клиентов:")
    for session_name, client in clients.items():
        if client is None:
            print(f"  {session_name}: None")
        else:
            print(f"  {session_name}: {'Connected' if client.is_connected else 'Disconnected'}")


async def monitor_replies(client):
    """Асинхронный мониторинг сообщений."""
    try:
        print(f"[DEBUG] Начало мониторинга сообщений для клиента: {client}")

        @client.on_message()
        async def handle_message(message):
            try:
                user_id = message.from_user.id
                text = message.text.strip().lower()
                print(f"[DEBUG] Получено сообщение от {user_id}: {text}")
            except Exception as e:
                print(f"[ERROR] Ошибка при обработке сообщения: {e}")

        print(f"[DEBUG] Мониторинг сообщений запущен.")
    except Exception as e:
        print(f"[ERROR] Ошибка в monitor_replies_for_account: {e}")
        raise


async def main():
    print("Запуск системы Telegram Automation...")

    reset_daily_sent()

    for account in ACCOUNTS:
        client = await initialize_client(account)

        if client is None:
            print(f"[ERROR] Клиент для {account['session_name']} не был создан. Пропускаем.")
            continue

        await run_account_workflow(client, account)

        delay = random.randint(*DELAY_BETWEEN_ACCOUNTS)
        print(f"Задержка перед следующим аккаунтом: {delay // 60} минут.")
        await asyncio.sleep(delay)

    print("Все аккаунты завершили рассылку, но продолжают мониторинг сообщений.")

    while True:
        await asyncio.sleep(20)


if __name__ == '__main__':
    asyncio.run(main())
