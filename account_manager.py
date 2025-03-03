from pyrogram import Client
from database import add_account
from proxy_manager import ACCOUNTS


def register_account(session_name, proxy=None):
    """Регистрирует новый аккаунт в системе."""
    with Client(ACCOUNTS[]['session_name'], api_id=ACCOUNTS[]['api_id'], api_hash=ACCOUNTS[]['api_hash'] as app:
        app.start()
        add_account(session_name, proxy)
        print(f"Аккаунт {session_name} успешно зарегистрирован.")
