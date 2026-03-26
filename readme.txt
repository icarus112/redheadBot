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

=================================================================================
УСТАНОВКА И НАСТРОЙКА

mkdir WorkTimeBot
git clone https://github.com/icarus112/WorkTimeBot.git   # установка
cd WorkTimeBot

python3 -m venv .venv     #активация окружения
source .venv/bin/activate

pip install --upgrade pip   #установка зависимостей
pip install -r requirements.txt

touch .env  #создаем переменное окружение и заполяем:
DB_HOST=localhost
DB_PORT=[port]
DB_NAME=[name]
DB_USER=[user]
DB_PASS=[password]
TOKEN = [ваш тг токен]
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
BOT_PROXY=socks5://127.0.0.1:[порт твоего впн или прокси,
если не используешь можно не создавать]

Создаем docker-compose.yml пример:

services:
  db:
    image: postgres:16
    container_name: [имя контейнера]
    environment:
      POSTGRES_DB: [имя БД с .env]
      POSTGRES_USER: [юзер БД с .env]
      POSTGRES_PASSWORD: [пароль БД с .env]
    ports:
      - "[порт БД с .env]:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U [юзер БД с .env] -d [имя БД с .env]"]
      interval: 5s
      timeout: 3s
      retries: 20

volumes:
  pgdata:

docker-compose up -d   #поднимаем БД

#попробуй подключится к БД
psql -h localhost -p {DB_PORT} -U {DB_USER} -d {DB_NAME}

#если подключилось то все ок, и продолжаем

#инициализация БД
cd ~/BOTS/Experiment/redheadBot
python -m database.init_db

#Если бот запустился но не получается может быть проблема в том
#что авторизация прошло не полностью из-за ошибки

#запуск
python main.py

#если он работает теперь можно сделать что бы он работал 24/7
#создадим сервис

sudo nano /etc/systemd/system/SomeBot.service
вводим:
[Unit]
Description=Redhead Telegram Bot
After=network.target docker.service

[Service]
User=root
#ИЗМЕНИ ПУТЬ
WorkingDirectory=/root/BOTS/Experiment/redheadBot
ExecStart=/root/BOTS/Experiment/redheadBot/.venv/bin/python main.py
Restart=always
RestartSec=5

# чтобы .env работал(ПУТЬ ИЗМЕНИ)
EnvironmentFile=/root/BOTS/Experiment/redheadBot/.env

[Install]
WantedBy=multi-user.target

#запускаем
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable redheadbot
systemctl start redheadbot

#проверь
systemctl status redheadbot

-----Команды которые могут пригодится
journalctl -u redheadbot -f  #логи
ss -tulnp | grep [нужный порт поиск]

docker-compose down -v #остановка
docker-compose up -d  #запуск

P.S. этот бот не такой и большой и ничего особо не делает обычный CRUD, но здесь я много чего освоил и продолжу работу
над проектами побольше. Надеюсь этот маленький бот на начало чего-то большего)

27.03.2026 Шаназаров С.
