# Инструкция для развертывания

## 1. Настройка .env файла

Для настройки переменных окружения создайте файл .env в корне проекта. Вот пример содержимого:

SECRET_KEY= 
DATABASE_URL= 
MAIN_URL=http://localhost:8000

POSTGRES_HOST= 
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=

## 2. Сборка docker-compose:

    docker-compose up --build

## 3. Создание папки для бэкапа бд:

    mkdir -p /var/opt/pgbackups && chown -R 999:999 /var/opt/pgbackups

## 4. Выполнение миграций

    docker exec -it smit_backend alembic upgrade head

## 5. Тестирование

    Тестирование доступно в сваггере по адресу http://localhost:8000/docs/
    Можно создать грузы по /cargo/create/ и зарегистрироваться по /auth/register/