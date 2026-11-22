# payment_system

[Русский](README.ru.md)

<details>
<summary><span style="font-size: 24px;">Contents</span></summary>

- [payment\_system](#payment_system)
  - [Project description](#project-description)
  - [Environment variables](#environment-variables)
    - [Description of environment variables](#description-of-environment-variables)
      - [APP\_PORT](#app_port)
      - [APP\_TRANSACTION\_SECRET](#app_transaction_secret)
      - [DB\_HOST](#db_host)
      - [DB\_NAME](#db_name)
      - [DB\_PASSWORD](#db_password)
      - [DB\_PORT](#db_port)
      - [DB\_USER](#db_user)
      - [DB\_LOGGING](#db_logging)
      - [JWT\_ACCESS\_TTL](#jwt_access_ttl)
      - [JWT\_ALGORITHM](#jwt_algorithm)
      - [JWT\_SECRET\_KEY](#jwt_secret_key)
  - [Running the application](#running-the-application)
    - [Running the application with docker compose](#running-the-application-with-docker-compose)
    - [Running the application without docker](#running-the-application-without-docker)
  - [Test data](#test-data)
    - [User](#user)
    - [Account](#account)
  - [Preparing data for the /api/transactions endpoint](#preparing-data-for-the-apitransactions-endpoint)
    - [Payment to someone else's account](#payment-to-someone-elses-account)
  - [Tests](#tests)
    - [Running end-to-end tests](#running-end-to-end-tests)
    - [Running all tests](#running-all-tests)
    - [Layer boundaries](#layer-boundaries)

</details>


## Project description

A FastAPI application that simulates a simple payment system.
It provides a REST API for working with users, administrators,
accounts, and transfers.

Technology stack:
 - FastAPI
 - SQLAlchemy
 - Alembic
 - PostgreSQL
 - Docker compose


## Environment variables
The list of environment variables expected by the application is described in
the .env.example file. Environment variables can be configured in the .env
file. To do that, copy .env.example to .env and set
the environment variables in that file:

```bash
cp .env.example .env
```

Environment variables can also be configured without creating an ___.env___ file in
the project root directory. To do that, all environment variables can be
set as __environment variables__ or __shell variables__. For example,
with the ___export___ command (a built-in utility of the Linux Bash shell:
___export ENV_NAME=ENV_VALUE___), or in another available way.<br />

### Description of environment variables
#### APP_PORT
Default: __8000__ <br/>
The port the application will listen on

#### APP_TRANSACTION_SECRET
Default: __<not set>__ <br/>
Secret key for verifying a transaction signature

#### DB_HOST
Default: __postgres__ <br />
Database host. If the application will run in a docker container and the database
will also run in a docker container, the host value must store the name
of the database service described in the docker-compose file.

#### DB_NAME
Default: __payment_system_db__ <br />
Database name.

#### DB_PASSWORD
Default: __<not set>__ <br />
Database user password.

#### DB_PORT
Default: __5432__ <br />
Database port.

#### DB_USER
Default: __postgres__ <br />
Role name used to connect to the database.

#### DB_LOGGING
Default: __False__
Enable SQLAlchemy logging.

#### JWT_ACCESS_TTL
Default: __30__ <br />
Access JWT token lifetime in minutes.

#### JWT_ALGORITHM
Default: __HS256__ <br />
Hashing algorithm.

#### JWT_SECRET_KEY
Default: __<not set>__ <br />
Secret key for the jwt library.


## Running the application
### Running the application with docker compose
1. Configure the environment variables (see [Environment variables](#environment-variables)).
   Use the .env file option. Make sure the
   DB_HOST variable stores the name of the service described in docker-compose.yaml
    - DB_HOST=postgres
2. Start the application in a container
```bash
docker-compose --env-file .env up
```


### Running the application without docker
The steps below describe how to start the microservice. It is assumed that PostgreSQL
is already installed or running in a docker container.

The project uses the package and dependency manager
[poetry](https://python-poetry.org/).

Minimum python version: 3.13

1. Create a python virtual environment
```bash
python3 -m venv .venv
```
2. Activate the virtual environment
```bash
source .venv/bin/activate
```
3. Upgrade __pip__
```bash
python3 -m pip install --upgrade pip
```
4. Install __poetry__
```bash
pip install poetry
```
5. Install packages and dependencies
```bash
poetry install --no-root
```
6. Create the environment variables file (see ["Environment variables"](#environment-variables) for details)
```bash
cp .env.example .env
```
7. Apply migrations to the database
```bash
alembic upgrade head
```
8. Start the local server
```bash
uvicorn src.main:app
```


## Test data
### User
Description of the test user data

| id | email             | first_name | surname | last_name  | role  | password       |
|----|-------------------|------------|---------|------------|-------|----------------|
| 1  | admin@example.com | Admin      | user    | NULL       | ADMIN | admin_password |
| 2  | ivan@example.com  | Ivan       | Ivanov  | Ivanovich  | USER  | user_password  |

### Account
Description of the test user account data
| id | balance | user_id |
|----|---------|---------|
| 1  | 50      | 2       |


## Preparing data for the /api/transactions endpoint

The script builds the JSON for `POST /transactions` and signs it with the
`APP_TRANSACTION_SECRET` secret from `.env`.

```bash
poetry run python scripts/prepare_transaction.py
```

By default, `user_id=2`, `account_id=2`, `amount=50`, and `transaction_id` is
a new UUID. Custom values are passed as flags:

```bash
poetry run python scripts/prepare_transaction.py --user-id 2 --account-id 1 --amount 50
```

### Payment to someone else's account

If the account `account_id` already exists and belongs to another user,
the payment is rejected with a `409` response. That account's balance and payment history
do not change. Someone else's account is not treated as an account of the user from the request, and a
new account with the same `account_id` cannot be created.

This is how the assignment item “check whether the user has such an account —
if not, create one” is read.


## Tests

End-to-end tests call the API through ASGI. They need a separate PostgreSQL so
they do not affect development data.


### Running end-to-end tests

#### 1. Environment variables

Copy the example test environment. In it, `DB_NAME` points to
a separate database `payment_system_test_db`, port `5433`. Do not replace these
values with the development database.

```bash
cp .env.test.example .env.test
```

#### 2. Data directory

The container creates `.test-data/postgres/` on the first start. If startup
fails with a permissions error or a missing directory, create it manually:

```bash
mkdir -p .test-data/postgres
```

#### 3. Start the test database

```bash
docker-compose --env-file .env.test -f compose.test.yaml up -d
```

#### 4. Apply migrations

A separate command is not needed. `pytest` itself runs `alembic upgrade head`
for the database from `.env.test`. Do not run `alembic` manually without these
variables: otherwise the migrations will go to the development database from `.env`.

#### 5. Run the tests

Dependencies, including pytest, are installed with the same command as for running
the application: `poetry install --no-root`.

```bash
poetry run pytest
```

#### Stopping the test database

```bash
docker-compose --env-file .env.test -f compose.test.yaml down
```


### Running all tests

Start the test database and run the tests:

```bash
docker-compose --env-file .env.test -f compose.test.yaml up -d

poetry run pytest
```

Stop the test database after the run:

```bash
docker-compose --env-file .env.test -f compose.test.yaml down
```

### Layer boundaries

`import-linter` checks the whole `src` package. Every module belongs to one layer:
`main`, `bootstrap`, `presentation`, `infrastructure`, `application`, or
`domain`. `presentation` and `infrastructure` do not import each other.

```bash
poetry run lint-imports
```

The same check runs before a commit if the hook is installed:

```bash
poetry run pre-commit install
```
