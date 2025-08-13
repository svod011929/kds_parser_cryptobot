#!/bin/bash

# Установка Python 3.12
echo "🛠 Установка Python 3.12..."
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt install -y python3.12 python3.12-venv

# Создание виртуального окружения
echo "💻 Создание виртуального окружения..."
python3.12 -m venv venv
source venv/bin/activate

# Установка зависимостей
echo "📦 Установка зависимостей..."
pip install telethon regex requests

# Запрос данных для конфигурации
echo "🛠 Конфигурация CryptoBot Parser"
echo "--------------------------------"

# Запрос данных для парсера
echo "🔑 Введите данные для парсера:"
read -p "API ID парсера: " api_id_parser
read -p "API HASH парсера: " api_hash_parser

# Запрос данных для активатора
echo -e "\n🔑 Введите данные для активатора:"
read -p "API ID активатора: " api_id_activator
read -p "API HASH активатора: " api_hash_activator

# Запрос данных каналов
echo -e "\n📢 Введите настройки каналов:"
read -p "Username канала для логов (без @): " channel
read -p "Username для автовывода (без @): " avto_vivod_tag

# Настройки капчи
echo -e "\n🤖 Настройки капчи:"
read -p "API-ключ OCR сервиса: " ocr_api_key

# Создание конфигурационного файла
echo "💾 Создание config.py..."
cat > config.py << EOF
# config.py — настройки аккаунтов

# Парсер (первый аккаунт)
api_id_parser = $api_id_parser
api_hash_parser = '$api_hash_parser'

# Активатор (второй аккаунт)
api_id_activator = $api_id_activator
api_hash_activator = '$api_hash_activator'

# Канал с логами
channel = '$channel'

# Автовывод средств
avto_vivod = True
avto_vivod_tag = '$avto_vivod_tag'

# Автоотписка от каналов
avto_otpiska = True

# Обход капчи
anti_captcha = True
ocr_api_key = '$ocr_api_key'
EOF

echo -e "\n✅ Установка завершена!"
echo "Конфигурация сохранена в config.py"
echo "Запустите бота командой: python main.py"
