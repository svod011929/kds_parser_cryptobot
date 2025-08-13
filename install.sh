#!/bin/bash

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    echo "Запустите скрипт с правами root: sudo ./install.sh"
    exit 1
fi

# Установка зависимостей
echo "Установка системных зависимостей..."
apt update
apt install -y git python3.12 python3.12-venv

# Клонирование репозитория
echo "Клонирование репозитория..."
git clone https://github.com/svod011929/kds_parser_cryptobot.git /opt/kds_parser
cd /opt/kds_parser

# Создание виртуального окружения
echo "Создание виртуального окружения..."
python3.12 -m venv venv
source venv/bin/activate

# Установка Python-зависимостей
echo "Установка Python-зависимостей..."
pip install --upgrade pip
pip install telethon regex requests

# Запрос конфигурационных данных
echo "Настройка конфигурации..."
read -p "API ID для парсера: " api_id_parser
read -p "API Hash для парсера: " api_hash_parser
read -p "API ID для активатора: " api_id_activator
read -p "API Hash для активатора: " api_hash_activator
read -p "Канал для логов (без @): " channel
read -p "Telegram username для автовывода (без @): " avto_vivod_tag
read -p "API ключ для OCR (оставьте пустым, если не требуется): " ocr_api_key

# Создание config.py
echo "Создание файла конфигурации..."
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

# Проверка и авторизация сессий
echo "Проверка файлов сессий..."
if [ ! -f "parser.session" ] || [ ! -f "activator.session" ]; then
    echo "Запуск процесса авторизации..."
    sudo -u $SUDO_USER /opt/kds_parser/venv/bin/python /opt/kds_parser/main.py --auth-only
    
    # Проверка успешности авторизации
    if [ ! -f "parser.session" ] || [ ! -f "activator.session" ]; then
        echo "⚠️ Внимание: Авторизация не завершена!"
        echo "Для завершения авторизации выполните:"
        echo "cd /opt/kds_parser && sudo venv/bin/python main.py --auth-only"
    else
        echo "✅ Авторизация успешно завершена!"
    fi
else
    echo "✅ Файлы сессий уже существуют, авторизация не требуется"
fi

# Инструкция для пользователя
echo -e "\n\x1B[1m✅ Установка завершена!\x1B[0m"
echo "Для запуска парсера выполните:"
echo "cd /opt/kds_parser"
echo "source venv/bin/activate"
echo "python main.py"

echo -e "\n\x1B[1m🔧 Для автозапуска создайте systemd сервис:\x1B[0m"
echo "1. Создайте файл сервиса:"
echo "   sudo nano /etc/systemd/system/kds_parser.service"
echo "2. Вставьте следующую конфигурацию:"
cat << EOF

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

[Install]
WantedBy=multi-user.target
EOF

echo -e "\n3. Активируйте сервис:"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable kds_parser.service"
echo "   sudo systemctl start kds_parser.service"
echo "4. Просмотр логов: journalctl -u kds_parser.service -f"
