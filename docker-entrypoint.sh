#!/bin/sh

echo "Setup Schema"
flask setup_schema

echo "Running Migrations"
flask db upgrade

echo "Create PG Function"
flask create_pg_function

exec "$@"
