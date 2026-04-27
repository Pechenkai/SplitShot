# Contributing to SplitShot

Документ описывает базовый рабочий процесс для разработки SplitShot: как поднять проект, где лежит код, как запускать миграции и тесты.

## Стек проекта

- Backend: FastAPI, SQLAlchemy 2 async, Pydantic, Alembic.
- Database: PostgreSQL 16.
- Frontend: статические файлы в `frontend/`, которые отдаются FastAPI.
- Tests: pytest, pytest-asyncio, httpx.
- Python: 3.10+, в CI используется Python 3.12.

## Структура репозитория

```
app/
  api/             # FastAPI routers and HTTP handlers
  db/models/       # SQLAlchemy ORM models
  repositories/    # Data access layer
  schemas/         # Pydantic request/response schemas
  services/        # Business logic
  seeds/           # Seed data helpers
  main.py          # FastAPI app entry point
alembic/           # Database migrations
frontend/          # Static frontend
tests/             # Unit, API and repository tests
docker/            # Docker helper scripts
```

Основная зависимость слоев:

```
API -> schemas/repositories/services -> db/models -> database
```

HTTP-логику держите в app/api/, работу с БД - в app/repositories/, бизнес-правила - в app/services/. Не смешивайте SQLAlchemy-модели и Pydantic-схемы: ORM-модели живут в app/db/models/, схемы API - в app/schemas/.

## Быстрый старт через Docker

1. Скопируйте переменные окружения:

```
cp .env.example .env
```
2. Поднимите backend и PostgreSQL:
```
docker compose up --build
```

По умолчанию backend будет доступен на порту из BACKEND_PORT в .env.example, то есть:
```
http://localhost:8002
```
API документация:
```
http://localhost:8002/docs
```
Healthcheck:
```
http://localhost:8002/health
```

## Локальный запуск без Docker backend

1. Создайте виртуальное окружение:
```
python -m venv .venv
source .venv/bin/activate
```
2. Установите зависимости:
```
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```
3. Поднимите только PostgreSQL:
```
docker compose up -d db
```
4. Примените миграции:
```
alembic upgrade head
```
5. Запустите приложение:
```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Локальные настройки берутся из .env. Для стандартного Docker PostgreSQL используйте URL вида:
```
DATABASE_URL=postgresql+asyncpg://splitshot:splitshot@localhost:5433/splitshot
TEST_DATABASE_URL=postgresql+asyncpg://splitshot:splitshot@localhost:5433/splitshot_test
```
## Миграции базы данных

После изменения SQLAlchemy-моделей в app/db/models/ создайте миграцию:
```
alembic revision --autogenerate -m "describe change"
```
Проверьте сгенерированный файл в alembic/versions/: автогенерация не всегда корректно отражает сложные изменения. Затем примените миграции:
```
alembic upgrade head
```
Откат на одну миграцию:
```
alembic downgrade -1
```
Перед pull request миграции должны применяться на чистую базу без ручных SQL-команд.

## Тесты

Тесты используют TEST_DATABASE_URL. Если база поднята через docker compose up -d db, тестовая БД splitshot_test создается init-скриптом контейнера.

Запуск всех тестов:
```
python -m pytest
```
Короткий вывод:
```
python -m pytest -q
```
Запуск отдельного файла:
```
python -m pytest tests/test_splitter.py
```
Фикстуры в tests/conftest.py перед тестовой сессией прогоняют Alembic-миграции на TEST_DATABASE_URL, а между тестами очищают таблицы.

## Как добавлять новый API ресурс

1. Добавьте или обновите ORM-модель в app/db/models/.
2. Зарегистрируйте модельный модуль в app/db/models/__init__.py и, если нужно для Alembic, в alembic/env.py.
3. Добавьте Pydantic-схемы в app/schemas/.
4. Добавьте репозиторий в app/repositories/.
5. Добавьте router в app/api/.
6. Подключите router в app/api/router.py.
7. Создайте Alembic-миграцию.
8. Добавьте тесты в tests/.

## Правила разработки

- Не коммитьте .env, .venv/, __pycache__/, .pytest_cache/, build-артефакты и локальные файлы IDE.
- Держите обработчики FastAPI тонкими: в них должна быть валидация HTTP-входа, вызов репозитория/сервиса и формирование ответа.
- Для денежных значений используйте Decimal, а не float.
- Для доступа к БД используйте async SQLAlchemy session из зависимостей/фикстур проекта.
- Любое изменение схемы БД сопровождайте Alembic-миграцией.
- Новое поведение покрывайте тестами на ближайшем уровне: service/repository/API.
- Перед отправкой изменений запускайте python -m pytest -q.

## CI

GitHub Actions запускает тесты на Python 3.12 с PostgreSQL 16. Pipeline:

1. Устанавливает зависимости .[dev].
2. Создает тестовую базу splitshot_test.
3. Применяет alembic upgrade head.
4. Запускает python -m pytest -q.

Локально полезно повторять те же шаги перед отправкой pull request.

## Работа с frontend

Файлы frontend лежат в frontend/ и отдаются backend-приложением:

- / возвращает frontend/index.html;
- /static/... отдает статические файлы из frontend/.

Если меняете frontend/app.js, frontend/styles.css или frontend/index.html, проверяйте результат через запущенный FastAPI backend в браузере.