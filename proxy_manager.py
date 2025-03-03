ACCOUNTS = [
    {
        "session_name": "",
        "api_id": 2219833,
        "api_hash": "",
        "proxy":  {
    "scheme": "",
    "hostname": "",
    "port": 1,
    "username": "",
    "password": "",
}
    },

]
MESSAGE_TEMPLATES = [

    'Привет! Мы продаём электронику телефоны ,планшеты, приставки и прочее по отличным ценам. Если интересно, пиши "да", пришлём приглашение в наш канал!',
    'Привет! Если занимаешь продажей электроники ,то могу пригласить тебя в наш канал . Пиши "да" и вышлю пришлашение !',
    'Привет! Мы продаем электронику лотами, еcли интерсно, пиши "да", отправлю тебе ссылку в наш закрытый канал.',

]
AUDIO_TEMPLATES = [
    '5357062843730516691.ogg',
    '1.mp3',
    '5361607967101706564.ogg'
]
REPLY_MESSAGE_TEMPLATES_GOOD =[
    'Отлично! Переходите сюда https://t.me/gadgetsOpt',
    'Лови https://t.me/gadgetsOpt'
    'держи https://t.me/gadgetsOpt'
    'Заходи скорее https://t.me/gadgetsOpt'
    'Круто, тогда переходи сюда https://t.me/gadgetsOpt'
    'Присоединяйся https://t.me/gadgetsOpt'
    'Канал возможностей - https://t.me/gadgetsOpt'
]
REPLY_MESSAGE_TEMPLATES_SAD =[
    'Упускаешь возможность'
    'Жаль, а сейчас сезон скидок'
    'Хорошо'
    'Ладно, это твой выбор'
    'Всегда работаем, если захочешь присоединиться, тогда пиши "да"'
]


_index = -1


def get_next_account():
    global _index
    _index = (_index + 1) % len(ACCOUNTS)
    return ACCOUNTS[_index]
