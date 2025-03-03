from database import get_users_for_messaging, update_user_status, update_account_sent_today, reset_daily_sent, update_user_account_session
import random
from proxy_manager import get_next_account, MESSAGE_TEMPLATES, AUDIO_TEMPLATES
import asyncio


DELAY_RANGE = (40, 60)


async def send_message(client, user_id, message, account_session):
    try:
        await client.send_message(user_id, message)  # Добавлено await
        update_user_status(user_id, "sent")
        update_user_account_session(user_id, account_session)
        print(f'ПОЛЬЗОВАТЕЛЮ ПРИСВОЕНА {user_id}: {account_session}')
        return True
    except Exception as e:
        print(f"Ошибка отправки сообщения пользователю {user_id}: {e}")
        return False


async def send_audio(client, user_id, audio_path):
    """Отправляет аудиофайл пользователю."""
    try:
        await client.send_audio(user_id, audio_path)  # Добавьте await
        return True
    except Exception as e:
        print(f"Ошибка отправки аудио пользователю {user_id}: {e}")
        return False



async def start_sending_messages(client, group_name, account):
    """Основной цикл рассылки сообщений."""

    users = get_users_for_messaging(limit=150)

    print(f"[DEBUG] Список пользователей для рассылки: {users}")
    for user_id, username in users:
        try:
            message = random.choice(MESSAGE_TEMPLATES)
            aort = random.randint(0, 5)
            if aort <= 1:
                await send_message(client, user_id, message, account_session=account['session_name'])
                update_user_status(user_id, "sent")
                update_account_sent_today(account['session_name'], 1)
            else:
                if AUDIO_TEMPLATES:
                    message = random.choice(AUDIO_TEMPLATES)
                    await send_audio(client, user_id, message)
                    update_account_sent_today(account['session_name'], 1)

            await asyncio.sleep(random.randint(*DELAY_RANGE))

            print(f"Аккаунт {account['session_name']} завершил рассылку.")
        except Exception as e:
            if "400" in str(e):
                print(f"[ERROR] Аккаунт {account['session_name']} ограничен. Переход к следующему аккаунту.")
                return False
            else:
                print(f"[ERROR] Ошибка отправки пользователю {user_id}: {e}")
                await asyncio.sleep(random.randint(*DELAY_RANGE))
                return True

