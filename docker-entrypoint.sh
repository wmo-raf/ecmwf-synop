#!/bin/sh

# Migrate db
echo "Running Migrations"
flask db upgrade
flask setup_db

exec "$@"
