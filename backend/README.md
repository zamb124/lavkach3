# SUKA - Платформа для управления предприятием





### Справка по архитектуре сервиса
Особенностью приложения является то, что каждый сервис знает **всё** или почти всё про модели друг друга.
Это даёт возможность построения микросервисного приложения с простым по реализации фронтом.

Обращение к модели идёт с помощью env.

[Env](/app/bff/bff_server.py) содержит в себе все модели всех приложений и адаптеры к ним.


#### Adapter 
[Adapter](/app/bff/adapters/basic_adapter.py) - это общедоступные операции, предоставляемые конкретным приложением для других. Является RPC-методом, клиент не знает об http-запросах.
#### Service
[Service](/app/basic/company/services/company_service.py) - это служба, реализующая бизнес-функции, как правило, над объектами. Используется только внутри приложения.

#### Api
[Api](/app/basic/company/api) - это точка входа для http, как правило, вызывается через адаптер.

#### Schemas
[Schemas](/app/basic/company/schemas) для CRUD операций + Filter, используется в основном для фронта.

#### Models
[Models](/app/basic/company/models) - хранимая табличка в базе данных в терминах SQLAlchemy.


То есть каждый сервис устроен так:
- model_scope_1 (модуль приложения)
    - api
    - services
    - schemas 
    - models
  
[//]: # (    ... permissions...)
- model_scope_2

  - ...

# Настройка проекта локально

Запуск Базы данных
```bash
version: "3.12"
services:
  db:
    image: postgres:15
    container_name: db_app
    command: -p 5433
    expose:
      - 5433
    env_file:
      - .env-docker
    ports:
      - 5433:5433
```
Зависимости:
```bash
pip install -r requirements.txt
```

### .env
- Нужо добать файл .env в корень проекта
```.env
DB_HOST=XXX
DB_PORT=XXX
DB_NAME=XXX
DB_USER=XXX
DB_PASS=XXX
POSTGRES_DB=XXX
POSTGRES_USER=XXX
POSTGRES_PASSWORD=XXX
ENV=local
DEBUG=True
JWT_SECRET_KEY=SECRET
JWT_ALGORITHM=HS256
SENTRY_SDN=None
REDIS_HOST=XXX
REDIS_PORT=XXX
REDIS_PASSWORD=XXX
REDIS_SSL=True
SMTP_USER=XXX
SMTP_PASSWORD=XXXXXXXXX
BASIC_DOMAIN=127.0.0.1
BUS_DOMAIN=127.0.0.1
SUPERUSER_EMAIL=XXX
SUPERUSER_PASSWORD=XXX
```

### Миграции
- Запуск миграций
``` bash
cd backend
alembic init alembic
mkdir alembic/versions
alembic revision --autogenerate -m "init"
```
Если нужно накатить тестовые данные, то нужно запустить

``` bash
cp migrations/testing_migrate.py migrations/versions/testing_migrate.py
```
так же заменить в  тестовой миграции на id говой миграции:
- down_revision = '6ea1b38aba41' 
- depends_on = '6ea1b38aba41' 

После этого 
```bash
alembic upgrade head
```

## Запуск самих сервисов
### Сервис BASIC
Сервис отвечающий за мастер данные 
```bash
uvicorn app.basic.basic_server:app --port 8001
```

### Сервис JOBS
Сервис отвечающий за разбор задач в очередях 
```bash
taskiq worker core.helpers.broker.tkq:broker
```

### Сервис BUS
Сервис отвечающий за отправку сообщений с пользователями
```bash
uvicorn app.bus.bus_server:app --port 8099 --lifespan on
```

### Сервис INVENTORY
Сервис управление материалами и товарами обьекта
```bash
uvicorn app.inventory.inventory_server:app --port 8002
```