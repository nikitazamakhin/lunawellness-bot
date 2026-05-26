#!/bin/bash

# 🤖 LUNA Bot Deployment Script
# Деплой Telegram бота на VPS

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🤖 LUNA Bot Deployment"
echo "======================"
echo ""

# Проверка наличия Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git не установлен. Запустите setup-vps.sh сначала${NC}"
    exit 1
fi

# Шаг 1: Клонирование репозитория (если еще не клонирован)
if [ ! -d "/root/luna-bot" ]; then
    echo -e "${YELLOW}[1/7] Клонирование репозитория...${NC}"
    cd /root
    git clone https://github.com/nikitazamakhin/lunawellness.git
    mv lunawellness/luna-bot /root/luna-bot
    rm -rf lunawellness
else
    echo -e "${YELLOW}[1/7] Обновление репозитория...${NC}"
    cd /root/luna-bot
    git pull
fi

cd /root/luna-bot

# Шаг 2: Создание virtual environment
echo -e "${YELLOW}[2/7] Создание virtual environment...${NC}"
python3.11 -m venv venv

# Шаг 3: Активация venv и установка зависимостей
echo -e "${YELLOW}[3/7] Установка зависимостей...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Шаг 4: Проверка .env файла
echo -e "${YELLOW}[4/7] Проверка .env файла...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}⚠️  .env файл не найден!${NC}"
    echo "Создаю шаблон .env файла..."
    cat > .env << 'EOF'
# Telegram Bot Token
BOT_TOKEN=your_bot_token_here

# Odoo Integration
ODOO_INTEGRATION_ENABLED=True
ODOO_API_URL=https://production-url.odoo.com/api
ODOO_API_TOKEN=your_token_here

# Database
DATABASE_PATH=bot/data/luna_bot.db
EOF
    echo -e "${YELLOW}⚠️  Заполни .env файл и запусти скрипт снова${NC}"
    exit 1
fi

# Шаг 5: Создание директорий
echo -e "${YELLOW}[5/7] Создание необходимых директорий...${NC}"
mkdir -p logs
mkdir -p bot/data
mkdir -p backups

# Шаг 6: Инициализация базы данных
echo -e "${YELLOW}[6/7] Инициализация базы данных...${NC}"
python3 -c "from bot.database.db import init_db; init_db()" || echo "База уже инициализирована"

# Шаг 7: Установка systemd service
echo -e "${YELLOW}[7/7] Установка systemd service...${NC}"
sudo cp deploy/luna-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable luna-bot
sudo systemctl restart luna-bot

echo ""
echo -e "${GREEN}✅ Деплой завершен!${NC}"
echo ""
echo "Проверь статус бота:"
echo "  sudo systemctl status luna-bot"
echo ""
echo "Посмотри логи:"
echo "  sudo journalctl -u luna-bot -f"
echo "  или"
echo "  tail -f logs/bot.log"
echo ""
