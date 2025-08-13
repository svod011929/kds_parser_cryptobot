# 🚀 Автопарсер Telegram-чеков CryptoBot на Python + Telethon

<p align="center">
  <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdDd1dXQ5a2J2dHl0aHVhcnJ5dGJ0d3Zjd3Ntbm5zcHl1bDZtb2FqbyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/coxQHKvGtqHwQNPS0s/giphy.gif" width="400" alt="Crypto Bot Animation">
</p>

## 💻 Технологии

<table align="center">
  <tr>
    <td align="center" width="200">
      <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" width="80">
      <br>
      <strong>Python</strong>
      <br>
      <span>Версия 3.12</span>
    </td>
    <td align="center" width="200">
      <img src="https://avatars.githubusercontent.com/u/9887454?s=48&v=4" width="80">
      <br>
      <strong>Telethon</strong>
      <br>
      <span>Асинхронный API</span>
    </td>
    <td align="center" width="200">
      <img src="https://cdn-icons-png.flaticon.com/512/5376/5376259.png" width="80">
      <br>
      <strong>OCR API</strong>
      <br>
      <span>Распознавание капчи</span>
    </td>
  </tr>
</table>

## 🔍 Описание
Автоматический инструмент для сбора и активации Telegram-чеков с использованием двух аккаунтов для максимальной безопасности:

- **Парсер** непрерывно мониторит чаты
- **Активатор** мгновенно обрабатывает найденные чеки

Оптимизированная скорость работы предотвращает блокировки аккаунтов и ограничения в чатах.

## ✨ Ключевые функции
- ⚡ Мгновенная активация чеков при появлении
- 🔑 Автоматическое распознавание паролей
- 🤖 Интеграция с OCR-сервисами для обхода капчи
- 💸 Ежедневный автовывод средств
- 📤 Автоматические отчеты в ваш канал
- 🧹 Самоочистка от неактивных каналов
- 🛡️ Разделение функционала между двумя аккаунтами

---

## ⚙️ Установка и настройка

### Для сервера Ubuntu
```bash
# Скачать и запустить установщик
wget https://raw.githubusercontent.com/svod011929/kds_parser_cryptobot/main/installer.sh
chmod +x installer.sh
./installer.sh
```
📌 *Установщик автоматически выполнит:*
- _Установку Python 3.12_
- _Инсталляцию зависимостей_
- _Настройку конфигурационного файла_

### Для Windows
1. **Скачайте архив проекта**  
   Нажмите `Code` → `Download ZIP` вверху справа на GitHub

2. **Установите Python 3.12**  
   - Скачайте [официальный установщик](https://python.org/downloads)
   - **Обязательно:** Отметьте ☑️ `Add Python to PATH`

3. **Откройте терминал в папке проекта**  
   - Распакуйте архив (например, в `C:\Projects\cryptobot`)
   - Перейдите в распакованную папку
   - В адресной строке проводника введите `cmd` и нажмите Enter

4. **Установите зависимости**  
```cmd
pip install telethon regex requests
```

5. **Настройте конфигурационный файл**  
   Откройте файл `config.py` и заполните по примеру:
   ```python
   api_id_parser = 1234567
   api_hash_parser = 'ваш_api_hash'
   api_id_activator = 7654321
   api_hash_activator = 'ваш_api_hash'
   channel = 'ваш_канал_логов'
   avto_vivod_tag = 'ваш_username'
   ocr_api_key = 'ваш_ключ_ocr'
   ```

---

## ⚡ Запуск программы
```bash
python main.py
```
[Пример работы](https://prnt.sc/krJYd3i9JAG7)

---

## ⚠️ Требования перед запуском
1. Два активных Telegram-аккаунта
2. API-ключи с [my.telegram.org](https://my.telegram.org)
3. Ключ для OCR-сервиса (рекомендуем [cap.guru](https://cap.guru) или [ocr.space](https://ocr.space/))

---

## 📄 Пример полной конфигурации
```python
# config.py — обязательные настройки

# Парсер (первый аккаунт)
api_id_parser = 1234567
api_hash_parser = 'a1b2c3d4e5f6g7h8i9j0'

# Активатор (второй аккаунт)
api_id_activator = 7654321
api_hash_activator = '0j9i8h7g6f5e4d3c2b1a'

# Канал для логов (без @)
channel = 'crypto_logs_channel'

# Автовывод средств
avto_vivod = True  # Включить ежедневный вывод
avto_vivod_tag = 'my_crypto_wallet'  # Ваш username

# Автоотписка от неактивных каналов
avto_otpiska = True

# Обход капчи
anti_captcha = True
ocr_api_key = '123abc456def789ghi'  # Ваш OCR API ключ
```

---

## 🌟 Поддержка и сотрудничество

<div align="center">
  
### ✨ Свяжитесь со мной

[![Telegram Contact](https://img.shields.io/badge/Telegram-@KodoDrive-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/KodoDrive)
[![Email](https://img.shields.io/badge/Email-business@example.com-7B68EE?style=for-the-badge&logo=gmail&logoColor=white)](mailto:bussines@kododrive-devl.ru)

</div>

<div align="center">
  <table>
    <tr>
      <td align="center" width="140">
        <img src="https://api.iconify.design/fluent-emoji-flat:sparkles.svg?width=60&height=60" alt="Sparkles">
        <br><strong>Поддержка</strong>
      </td>
      <td align="center" width="140">
        <img src="https://api.iconify.design/fluent-emoji-flat:briefcase.svg?width=60&height=60" alt="Briefcase">
        <br><strong>Сотрудничество</strong>
      </td>
      <td align="center" width="140">
        <img src="https://api.iconify.design/fluent-emoji-flat:gear.svg?width=60&height=60" alt="Gear">
        <br><strong>Настройка</strong>
      </td>
    </tr>
  </table>
</div>

<div align="center" style="margin-top: 20px; font-size: 1.2rem;">

📬 **Telegram:** [@KodoDrive](https://t.me/KodoDrive)  
⏳ Отвечаю в течение 24 часов  
💼 Деловые предложения: bussines@kododrive-devl.ru

</div>

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&pause=1000&color=7B1FA2&center=true&vCenter=true&width=500&lines=%D0%93%D0%BE%D1%82%D0%BE%D0%B2+%D0%BA+%D1%81%D0%BE%D1%82%D1%80%D1%83%D0%B4%D0%BD%D0%B8%D1%87%D0%B5%D1%81%D1%82%D0%B2%D1%83%21;%D0%9F%D0%B8%D1%88%D0%B8+%D0%B2+Telegram+%F0%9F%93%A7;%D0%9E%D1%82%D0%B2%D0%B5%D1%87%D0%B0%D1%8E+%D0%B2+%D1%82%D0%B5%D1%87%D0%B5%D0%BD%D0%B8%D0%B5+24+%D1%87%D0%B0%D1%81%D0%BE%D0%B2+%F0%9F%95%92" alt="Typing SVG">
</p>

<p align="center">
  <img src="https://komarev.com/ghpvc/?username=svod011929&repo=kds_parser_cryptobot&label=Просмотры+репозитория&color=7b1fa2&style=for-the-badge&labelColor=5d4037" width="400" height="50" alt="Repository views">
</p>
