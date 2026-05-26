#!/bin/bash

# 🚀 LUNA Bot VPS Setup Script
# Автоматическая настройка VPS для LUNA Wellness бота

set -e

echo "🌙 LUNA Wellness Bot - VPS Setup"
echo "================================="
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Шаг 1: Обновление системы
echo -e "${YELLOW}[1/6] Обновление системы...${NC}"
sudo apt update && sudo apt upgrade -y

# Шаг 2: Установка Python 3.11
echo -e "${YELLOW}[2/6] Установка Python 3.11...${NC}"
sudo apt install -y python3.11 python3.11-venv python3-pip git curl

# Шаг 3: Установка дополнительных пакетов
echo -e "${YELLOW}[3/6] Установка дополнительных пакетов...${NC}"
sudo apt install -y supervisor nginx certbot python3-certbot-nginx

# Шаг 4: Настройка firewall
echo -e "${YELLOW}[4/6] Настройка firewall...${NC}"
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
echo "y" | sudo ufw enable

# Шаг 5: Создание пользователя для бота (опционально)
echo -e "${YELLOW}[5/6] Создание структуры директорий...${NC}"
mkdir -p ~/luna-bot
mkdir -p ~/luna-bot/logs
mkdir -p ~/luna-bot/backups

# Шаг 6: Установка Node.js (для возможных future updates)
echo -e "${YELLOW}[6/6] Установка Node.js...${NC}"
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

echo ""
echo -e "${GREEN}✅ Базовая настройка VPS завершена!${NC}"
echo ""
echo "Следующие шаги:"
echo "1. Клонировать репозиторий бота"
echo "2. Настроить .env файл"
echo "3. Установить зависимости Python"
echo "4. Запустить бота через systemd"
echo ""
