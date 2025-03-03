from random import choice
from database import update_user_status, get_user_account_session
from proxy_manager import REPLY_MESSAGE_TEMPLATES_SAD, REPLY_MESSAGE_TEMPLATES_GOOD

VALID_RESPONSES = {"да", "нет"}
INVALID_RESPONSE_MESSAGE = "Ответьте на сообщение текстом: 'Да' или 'Нет'."


async def monitor_replies_for_account(client, clients):
    """Асинхронный мониторинг сообщений."""

    if not client.is_connected:
        try:
            await client.start()
            print(f"[INFO] Клиент {client} подключен для мониторинга.")
        except Exception as e:
            print(f"[ERROR] Не удалось подключить клиента {client}: {e}")
            return
    else:
        print(f"[INFO] Клиент {client} уже подключен. Продолжаем мониторинг.")

    @client.on_message()
    async def handle_message(h, message):
        try:
            user_id = message.from_user.id
            text = message.text.strip().lower()

            account_session = get_user_account_session(user_id=user_id)

            reply_client = clients.get(account_session)
            if reply_client == h:
                print(f"[DEBUG] Ответ от {user_id} через клиент {account_session}. Сообщение: {text}")
                if text in VALID_RESPONSES:
                    update_user_status(user_id, "replied", reply=text)

                    reply_message = (
                        choice(REPLY_MESSAGE_TEMPLATES_GOOD)
                        if text == "да"
                        else choice(REPLY_MESSAGE_TEMPLATES_SAD)
                    )
                    await reply_client.send_message(user_id, reply_message)
                else:
                    await reply_client.send_message(user_id, INVALID_RESPONSE_MESSAGE)
                    print(f"Неверный ответ от {user_id}.")
            else:
                print(f"[DEBUG] Ответ от {user_id} через клиент {account_session}. Сообщение: {text}")
                if text in VALID_RESPONSES:
                    update_user_status(user_id, "replied", reply=text)

                    reply_message = (
                        choice(REPLY_MESSAGE_TEMPLATES_GOOD)
                        if text == "да"
                        else choice(REPLY_MESSAGE_TEMPLATES_SAD)
                    )
                    async with reply_client:
                        await reply_client.send_message(user_id, reply_message)
                else:
                    async with reply_client:
                        await reply_client.send_message(user_id, INVALID_RESPONSE_MESSAGE)
                    print(f"Неверный ответ от {user_id}.")

        except Exception as e:
            print(f"[ERROR] Ошибка при обработке сообщения: {e}")
