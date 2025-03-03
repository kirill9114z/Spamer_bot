from database import add_user, add_group, update_group_last_updated


async def gather_users_from_group(group_name, client, account):
    """
    Получает список участников группы и добавляет их в базу данных.
    """

    try:

        print(f"Подключение к группе {group_name} с аккаунта {account['session_name']}...")
        group = await client.get_chat(group_name)
        print(group.id)
        add_group(group_name)

        print(f"Сбор участников группы {group.title}...")
        total_members = 0
        async for member in client.get_chat_members(group.id):  # Используем async for
            if not member.user.is_bot and not member.user.is_deleted:
                user_id = member.user.id
                username = member.user.username
                add_user(user_id, username, group_name)
                total_members += 1

        print(f"Сбор участников завершен. Добавлено {total_members} участников.")
        update_group_last_updated(group_name)
    except Exception as e:
        print(f"Ошибка при сборе участников группы {group_name}: {e}")

