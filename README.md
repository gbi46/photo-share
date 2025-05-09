## DB install Guide

Create a Database. We use PostgreSQL
To create the DB you have to download and install PostgreSQL

```
https://www.postgresql.org/download/
```
Then open bash and connect to the DB server:

```
psql -U your_username
```

Run the command to create a DB

```
CREATE DATABASE <DB_NAME>
```

## Project Install guide

In bash terminal

```
git clone https://github.com/gbi46/photo-share.git
cd photo-share
poetry install
poetry shell
```

You need to create a .env file inside src/conf/.
If the project is in a pipeline state, create a .env.development file instead.
```
cd src/conf/
touch .env
```

### **structure of .env**

```
ENV_APP=development
DB_URL=postgresql+asyncpg://<USERNAME>:<PASSWORD>@<HOST>:<PORT>/<DB_NAME>

ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256
SECRET_KEY=your-super-secret

CLD_NAME=your-cloud-name
CLD_API_KEY=1234567890
CLD_API_SECRET=your-cloud-secret
```

Make the first migration to create tables

```
alembic upgrade head
```

## Running tests

```
pytest --cov
```

or for report with precision

```
coverage report --precision=2
```