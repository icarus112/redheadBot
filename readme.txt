этот бот создан для введение записей рабочих часов с его помощью можно добавлять, удалять, изменять записи
учитывать чаевые (или нет), удобный отчет по 15 дням месяца, в котором данные для введения статистики,
также все данные можно получить в виду excel(почему бы и нет)

===================================================================
То есть ВОЗМОЖНОСТИ:
Добавление рабочих часов
Учёт чаевых
Хранение данных в PostgreSQL
Экспорт отчётов в Excel
Работа через прокси (при необходимости)
Вывод данных в удобном варианте
Изменение данных в БД

===================================================================
ОСНОВНЫЕ ТЕХНОЛОГИИ:
Python
aiogram 3
sqlalchemy
postgresql
docker-compose
pandas
pytest
asyncpg

===================================================================
СТРУКТУРА:
app - все хендлеры и keyboards
database/
    -repos - функции для работы с БД
    -service - вызывает функции с repos, я их разделил для pytest
    Потому что иначе выходит ошибка по pytest
    db.py - создание сессии для БД
    docker-compose - конфиг для поднятия БД
    services:
  db:
    image: postgres:16
    container_name: redhead_postgres
    environment:
      POSTGRES_DB: tracker
      POSTGRES_USER: tracker_user
      POSTGRES_PASSWORD: tracker_pass
    ports:
      - "5433:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U tracker_user -d tracker"]
      interval: 5s
      timeout: 3s
      retries: 20

volumes:
  pgdata:

    funcs - функции для вычисления, парсинга текста
    init_db - инициализация БД
    insert_test - не используется(оставил для справки)
    models - модели таблиц для БД
    reports - тоже как funcs
test/
    *тесты(не все); conftest - надстройка для тестов
.env -
    DB_HOST=-
    DB_PORT=-
    DB_NAME=-
    DB_USER=-
    DB_PASS=-
    TOKEN = -
    DATABASE_URL = postgresql+asyncpg://-
    BOT_PROXY=socks5://127.0.0.1:{*порт который использует твой впн}
.gitignore -
    .venv/
    .venv/
    .env
    __pycache__/
    *.pyc
    *.pyo
    *.pyd
bfg-1.14.0.jar - для очитски истории если в github выложил то что не надо было
conf - конф для url базы данных
create_tables - не используется(оставил для справки)
main - "большой взрыв" проекта
requirements.txt - зависимости