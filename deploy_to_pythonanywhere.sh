#!/bin/bash

# Скрипт для деплоя на PythonAnywhere
# Использование: bash deploy_to_pythonanywhere.sh

echo "🚀 Начинаем деплой на PythonAnywhere..."

# 1. Коммит и пуш изменений
echo "📝 Коммитим изменения..."
git add .
git status

read -p "Введите сообщение коммита: " commit_message
git commit -m "$commit_message"

echo "⬆️ Пушим в GitHub..."
git push origin main

echo ""
echo "✅ Изменения загружены в GitHub!"
echo ""
echo "📋 Теперь выполните на PythonAnywhere в Bash консоли:"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "cd ~/qr_code_menu"
echo "git pull origin main"
echo "python manage.py collectstatic --noinput --clear"
echo "touch /var/www/\$(whoami)_pythonanywhere_com_wsgi.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "После выполнения этих команд очистите кэш браузера (Ctrl+Shift+R)"