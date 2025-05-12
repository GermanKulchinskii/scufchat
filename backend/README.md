## Fastapi GraphQL React chat web app
This app uses WebSocket to enable realtime message exchange, allows for private and group chats and offers basic chat admin functions

## Package requirements
```
fastapi>=0.115.11,<0.116.0
uvicorn>=0.34.0,<0.35.0
sqlalchemy>=2.0.38,<3.0.0
sqlmodel>=0.0.24,<0.0.25
alembic>=1.15.1,<2.0.0
psycopg2-binary>=2.9.10,<3.0.0
pyjwt[crypto]>=2.10.1,<3.0.0
passlib[bcrypt]>=1.7.4,<2.0.0
pydantic>=2.10.6,<3.0.0
pydantic-settings>=2.8.1,<3.0.0
strawberry-graphql>=0.262.5,<0.263.0
websockets>=15.0.1,<16.0.0
flake8>=7.2.0,<8.0.0
black>=25.1.0,<26.0.0
isort>=6.0.1,<7.0.0
pre-commit>=4.2.0,<5.0.0
```

## Deploy [![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
### Requirements
To deploy you'll need:
- [Python](https://www.python.org/downloads/release/python-3132/)
- An SQL database
- [Poetry](https://python-poetry.org/docs/)

### Steps
1. Pick a directory and do a ```git clone``` of this project
2. Create a .env file in project root
3. Fill it using .env.example as an example
4. Run 
```shell
poetry install --with development
```
5. Apply migrations 
```shell
poetry run alembic upgrade head
```
6. Start the project with
```shell
poetry run python fapigraphproject
```
