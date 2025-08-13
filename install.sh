#!/bin/bash

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    echo "Запустите скрипт с правами root: sudo ./install.sh"
    exit 1
fi

# Установка Python 3.12 и зависимостей
apt update
apt install -y git python3.12 python3.12-venv

# Клонирование репозитория
git clone https://github.com/svod011929/kds_parser_cryptobot.git /opt/kds_parser
cd /opt/kds_parser

# Создание виртуального окружения и установка зависимостей
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install telethon regex requests

# Запрос конфигурационных данных
read -p "API ID для парсера: " api_id_parser
read -p "API Hash для парсера: " api_hash_parser
read -p "API ID для активатора: " api_id_activator
read -p "API Hash для активатора: " api_hash_activator
read -p "Канал для логов (без @): " channel
read -p "Telegram username для автовывода (без @): " avto_vivod_tag
read -p "API ключ для OCR (оставьте пустым, если не требуется): " ocr_api_key

# Создание config.py
cat > config.py << EOF
# Настройки API для парсера
api_id_parser = $api_id_parser
api_hash_parser = '$api_hash_parser'

# Настройки API для активатора
api_id_activator = $api_id_activator
api_hash_activator = '$api_hash_activator'

# Канал с логами
channel = '$channel'

# Автовывод средств
avto_vivod = True
avto_vivod_tag = '$avto_vivod_tag'

# Автоотписка
avto_otpiska = True

# Поддержка капчи
anti_captcha = True
ocr_api_key = '$ocr_api_key'
EOF

# Создание systemd сервиса
cat > /etc/systemd/system/kds_parser.service << EOF
[Unit]
Description=KDS Parser CryptoBot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/kds_parser
ExecStart=/opt/kds_parser/venv/bin/python main.py
Restart=always
RestartSec=10
Environment="PYTHONUNBUFFERED=1"

# Переменные для обработки отсутствия сессий
ExecStartPre=/bin/sh -c 'if [ ! -f "parser.session" ] || [ ! -f "activator.session" ]; then echo "Обнаружены отсутствующие файлы сессий. Требуется повторная авторизация!"; rm -f parser.session activator.session; fi'

[Install]
WantedBy=multi-user.target
EOF

# Перезагрузка systemd и запуск сервиса
systemctl daemon-reload
systemctl enable kds_parser.service

echo "Установка завершена!"
echo "Для авторизации аккаунтов выполните:"
echo "systemctl start kds_parser.service"
echo "journalctl -u kds_parser.service -f"
