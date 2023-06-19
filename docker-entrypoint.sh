#!/bin/sh

# Migrate db
echo "Running Migrations"
flask db upgrade

exec "$@"
