# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \ 
    gcc \
    libpq-dev \
    && apt-get clean

# Указываем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Меняем рабочую директорию на директорию проекта, где находится manage.py
WORKDIR /app/blogicum

# Собираем статические файлы
RUN python manage.py collectstatic --noinput

# Указываем порт Gunicorn
EXPOSE 8000

# Запуск сервера через Gunicorn
CMD ["gunicorn", "blogicum.wsgi:application", "--bind", "0.0.0.0:8000"]