# Todo list API

[English version](https://github.com/BananfonBan/Todo-list-API/blob/main/README.md)

Простое RESTful API для ведения списка дел

![Static Badge](https://img.shields.io/badge/BananfonBan-Todo_list_API-Banan)

![GitHub top language](https://img.shields.io/github/languages/top/BananfonBan/Todo-list-API) ![GitHub](https://img.shields.io/github/license/BananfonBan/Todo-list-API)

![GitHub issues](https://img.shields.io/github/issues/BananfonBan/Todo-list-API)

![GitHub Repo stars](https://img.shields.io/github/stars/BananfonBan/Todo-list-API)

---

## [TL;DR](https://en.wikipedia.org/wiki/TL;DR)

Простое приложение для ведения списка дел. Идея и требования взяты из [этого проекта](https://roadmap.sh/projects/todo-list-api) с сайта [roadmap.sh](https://roadmap.sh)


## Описание 

Это RESTful API для управления списком задач (ToDos). API предоставляет возможность создавать, обновлять, удалять и просматривать задачи. Включает систему аутентификации на основе JWT, которая может работать как через HTTP-only cookies, так и через заголовки `Authorization`.


### Используемые технологии

[![Pydantic](https://img.shields.io/pypi/v/pydantic.svg?label=Pydantic&logo=pydantic)](https://github.com/samuelcolvin/pydantic) [![FastAPI](https://img.shields.io/pypi/v/fastapi.svg?label=FastAPI&logo=fastapi)](https://github.com/tiangolo/fastapi)

[![SQLAlchemy](https://img.shields.io/pypi/v/sqlalchemy.svg?label=SQLAlchemy&logo=sqlalchemy)](https://github.com/sqlalchemy/sqlalchemy) [![Alembic](https://img.shields.io/pypi/v/alembic.svg?label=Alembic&logo=alembic)](https://github.com/sqlalchemy/alembic)

[![SQLAlchemy](https://img.shields.io/pypi/v/PyJWT.svg?label=PyJWT&logo=PyJWT)](https://github.com/jpadilla/pyjwt)

Этот проект использует следующие технологии:
  
- **Pydantic**: Для валидации данных.

- **FastAPI**: Для создания эндпоинтов API.

- **SQLAlchemy**: Для работы с базой данных.

- **Alembic**: Для миграций базы данных.

- **PyJWT**: Для работы с JWT


## Функциональные возможности

1. **Управление задачами:**
    
    - Создание новых задач.
    - Просмотр списка задач.
    - Обновление существующих задач.
    - Удаление задач.
2. **Аутентификация и авторизация:**
    
    - Регистрация пользователей.
    - Аутентификация через JWT-токены:
        - Через HTTP-only cookies.
        - Через заголовок `Authorization`.


## Требования

### Зависимости

- Python 3.9+
- FastAPI
- SQLAlchemy
- Alembic
- PyJWT

### База данных

- PostgreSQL


## Установка

### Клонирование репозитория

```bash
git clone https://github.com/BananfonBan/Todo-list-API
cd Todo-list-API
```

### Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate  # Для Windows: venv\Scripts\activate
```

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Настройка окружения

В корне проекта есть пример необходимых переменных окружения:

```
# env.example
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=supersecretpassword
DB_NAME=mydb
SECRET_KEY=S8tqf6OIMaOAJrOa4m1tC0h2XiH/4yFX0ezcIto0gLU=
ALGORITHM=HS256
AUTH_METHOD=cookie
```

| Переменная         | Описание                                                                 |
|--------------------|-------------------------------------------------------------------------|
| `DB_HOST`          | Домен для подключения к базе данных (по умолчанию `localhost`)          |
| `DB_PORT`          | Порт базы данных (стандартный порт PostgreSQL — 5432)                  |
| `DB_USER`          | Имя пользователя базы данных                                            |
| `DB_PASS`          | Пароль для подключения к базе данных                                    |
| `DB_NAME`          | Название базы данных                                                    |
| `SECRET_KEY`       | Секретный ключ для работы JWT (генерируется командой `openssl rand -base64 32`)|
| `ALGORITHM`        | Алгоритм шифрования JWT (`HS256` можно оставить без изменения)                                         |
| `AUTH_METHOD`      | Метод авторизации (`cookie` или `header`)                               |

### Запуск

```bash
make run
```

По умолчанию приложение доступно на порту 8000

## API Документация

API документировано с помощью Swagger UI и доступно по адресу:
`http://localhost:8000/docs`


## Аутентификация

API поддерживает две системы аутентификации:

1. **Через HTTP-only cookies:**
    
    - После успешной аутентификации токен сохраняется в HTTP-only cookie с именем `access_token`.
    - Cookie автоматически отправляется с каждым запросом к серверу.
2. **Через заголовок `Authorization`:**
    
    - Токен должен быть передан в заголовке `Authorization` с префиксом `Bearer`.
    - Пример: `Authorization: Bearer <access_token>`.


## Roadmap

- [ ] Добавить тесты
- [ ] Добавить систему refresh токенов
- [ ] Создать Docker-образ приложения
- [ ] Добавить систему Rate Limiting и Throttling

## Лицензия

Этот проект распространяется под лицензией MIT. Подробнее см. [LICENSE](https://github.com/BananfonBan/Todo-list-API/blob/main/LICENSE).

## Авторы

- Egor - [BananfonBan](https://github.com/BananfonBan)

## Дополнительная информация

При написании этого приложения я старался разделить его на слои:
- Репозиторий (Repo, DAO) - Слой для работы с БД.
- Сервисы (Services) - Слой, который отвечает за "Бизнес логику"
- End-points - Интерфейс приложения (API)

Слои "общаются" между собой с помощью DTO (Data Transfer Object)

### Полезные ссылки

[Как правильно писать ТЗ на Python](https://habr.com/ru/articles/877180/)
[Про токены, JWT, авторизацию и аутентификацию](https://gist.github.com/artemonsh/34345edb40d9097f94bd54aa4b8313f6)
[Пример реализация авторизации и аутентификации через JWT](https://habr.com/ru/articles/829742/)

### Контакты

Если у вас есть вопросы или вы можете дать советы и критику, милости прошу в ТГ ([@BananfonBan](https://t.me/BananfonBan))
 