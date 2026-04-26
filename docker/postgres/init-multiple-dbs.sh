#!/bin/sh
set -eu

if [ -n "${POSTGRES_MULTIPLE_DATABASES:-}" ]; then
  echo "Creating multiple PostgreSQL databases: ${POSTGRES_MULTIPLE_DATABASES}"
  OLD_IFS="$IFS"
  IFS=','
  for db in $POSTGRES_MULTIPLE_DATABASES; do
    db_trimmed="$(echo "$db" | tr -d ' ')"
    if [ -n "$db_trimmed" ]; then
      psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
        CREATE DATABASE $db_trimmed;
EOSQL
    fi
  done
  IFS="$OLD_IFS"
fi
