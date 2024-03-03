#!/usr/bin/env bash

source ./venv/bin/activate
cd ./auth-service/src/

alembic revision --autogenerate -m "Init database"
alembic upgrade head
