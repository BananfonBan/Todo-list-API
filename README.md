# Todo list API
[Русская версия](https://github.com/BananfonBan/Todo-list-API/blob/main/dosc/ru/README.md)

![Static Badge](https://img.shields.io/badge/BananfonBan-Todo_list_API-Banan)

![GitHub top language](https://img.shields.io/github/languages/top/BananfonBan/Todo-list-API) ![GitHub](https://img.shields.io/github/license/BananfonBan/Todo-list-API)

![GitHub issues](https://img.shields.io/github/issues/BananfonBan/Todo-list-API)

![GitHub Repo stars](https://img.shields.io/github/stars/BananfonBan/Todo-list-API)

---

## [TL;DR](https://en.wikipedia.org/wiki/TL;DR)

This is a RESTful API for managing a to-do list. It allows users to create, update, delete, and view tasks. The idea and requirements are based on [this project](https://roadmap.sh/projects/todo-list-api) from [roadmap.sh](https://roadmap.sh).

---

## Description
This RESTful API allows you to manage a list of tasks (ToDos). It provides the ability to create, update, delete, and view tasks. The API includes an authentication system based on JWT, which supports two methods of authorization:
- Through HTTP-only cookies.
- Through the Authorization header.


## Features
1. Task Management:
    - Create new tasks.
    - View a list of tasks.
    - Update existing tasks.
    - Delete tasks.
2. Authentication and Authorization:
    - User registration.
    - Authentication via JWT tokens:
        - Through HTTP-only cookies.
        - Through the Authorization header.


## Technologies Used

[![Pydantic](https://img.shields.io/pypi/v/pydantic.svg?label=Pydantic&logo=pydantic)](https://github.com/samuelcolvin/pydantic) [![FastAPI](https://img.shields.io/pypi/v/fastapi.svg?label=FastAPI&logo=fastapi)](https://github.com/tiangolo/fastapi)

[![SQLAlchemy](https://img.shields.io/pypi/v/sqlalchemy.svg?label=SQLAlchemy&logo=sqlalchemy)](https://github.com/sqlalchemy/sqlalchemy) [![Alembic](https://img.shields.io/pypi/v/alembic.svg?label=Alembic&logo=alembic)](https://github.com/sqlalchemy/alembic)

[![SQLAlchemy](https://img.shields.io/pypi/v/PyJWT.svg?label=PyJWT&logo=PyJWT)](https://github.com/jpadilla/pyjwt)

This project uses the following technologies:

| Technology | Purpose                                      |
| ---------- | -------------------------------------------- |
| FastAPI    | For creating API endpoints                   |
| SQLAlchemy | For database operations                      |
| Alembic    | For database migrations                      |
| PyJWT      | For working with JSON Web Tokens (JWT)       |
| Pydantic   | For data validation and settings management. |



## Requirements

### Dependencies

Python 3.9+
FastAPI
SQLAlchemy
Alembic
PyJWT

### Database

PostgreSQL


## Installation


### 1. Clone the Repository

```bash
git clone https://github.com/BananfonBan/Todo-list-API
cd Todo-list-API
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
make install
```

### 4. Configure Environment Variables

Copy the example environment file and configure it:
```bash
cp env.example .env
```

Edit .env with your database credentials and other settings:

| Variable      | Description                                                                   | Example value         |
| ------------- | ----------------------------------------------------------------------------- | --------------------- |
| `DB_HOST`     | Database host (use `localhost` for local development).                        | `localhost`           |
| `DB_PORT`     | Database port (default for PostgreSQL is `5432`).                             | `5432`                |
| `DB_USER`     | Database username                                                             | `postgres`            |
| `DB_PASS`     | Database password                                                             | `supersecretpassword` |
| `DB_NAME`     | Database name                                                                 | `mydb`                |
| `SECRET_KEY`  | Secret key for JWT encryption. Generate one using: `openssl rand -base64 32` |                       |
| `ALGORITHM`   | Encryption algorithm for JWT (default is `HS256`)                             | `HS256`               |
| `AUTH_METHOD` | Method for user authentication (`cookie`or`header`).                        |         `cookie`              |

### Run the Application

Use make run to apply migrations and start the server:

```bash
make run
```

By default, the application will be available at `http://localhost:8000`.

## Docker

For convenient deployment, it is recommended to use Docker. The application can be run using `docker-compose`, which will automatically create containers for the API and PostgreSQL.

### Requirements

- Installed [Docker](https://docs.docker.com/get-docker/).
- Installed [Docker Compose](https://docs.docker.com/compose/install/).

### Running with Docker Compose

Some environment variables are predefined in the `docker-compose.yml`. All you need to do is:

1. Generate a secret key:
    ```bash
    openssl rand -base64 32
    ```

2. Replace the `SECRET_KEY` variable in the `docker-compose.yml` with your generated key:
    ```yaml
    - SECRET_KEY=your_secret_key_here
    ```

3. Start all services using the following command:
    ```bash
    docker-compose up -d
    ```

The application will be available at: [http://localhost:8000](http://localhost:8000).


## API Documentation
The API is documented using Swagger UI and is accessible at: `http://localhost:8000/docs`


## Authentication

The API supports two authentication methods:

1. HTTP-only Cookies:
    - After successful authentication, the token is stored in an HTTP-only cookie named access_token.
    - The cookie is automatically sent with each request to the server.
2. Authorization Header:
    - The token must be passed in the Authorization header with the Bearer prefix.
    - Example:
        ```bash
        Authorization: Bearer <your_jwt_token>
        ```


## Roadmap

- [x] Add unit tests.
- [ ] Implement refresh token functionality.
- [x] Create a Docker image for the application.
- [ ] Add rate limiting and throttling mechanisms.

## Contribution
Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a clear description of your changes.

## License

This project is licensed under the MIT License. See [LICENSE](https://github.com/BananfonBan/Todo-list-API/blob/main/LICENSE) for more details.

## Authors

- Egor - [BananfonBan](https://github.com/BananfonBan)

## Additional Information

This application follows a layered architecture:

- Repository Layer: Handles database interactions.
- Service Layer: Implements business logic.
- Endpoints Layer: Provides the API interface.

Layers communicate with each other using Data Transfer Objects (DTOs) to ensure loose coupling and maintainability.

### Useful Links

[How to Write Good Requirements for Python Projects](https://habr.com/ru/articles/877180/) (rus)
[Tokens, JWT, Authentication, and Authorization Explained](https://gist.github.com/artemonsh/34345edb40d9097f94bd54aa4b8313f6) (rus)
[Example Implementation of JWT Authentication](https://habr.com/ru/articles/829742/) (rus)

### Contact

If you have any questions, suggestions, or feedback, feel free to reach out via Telegram: [@BananfonBan](https://t.me/BananfonBan) .
