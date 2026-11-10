#!/usr/bin/env sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
alembic_bin=${ALEMBIC_BIN:-"$repo_root/backend/.venv/bin/alembic"}
database_url=${DB001_DATABASE_URL:-"postgresql+psycopg://enterprise_rag_dev:synthetic_only_not_secret@127.0.0.1:55433/enterprise_rag_dev"}

if [ ! -x "$alembic_bin" ]; then
  echo "Alembic executable not found: $alembic_bin" >&2
  echo "Set ALEMBIC_BIN to a Backend environment with the db extra installed." >&2
  exit 1
fi

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "Usage: $0 upgrade [revision] | rollback [revision]" >&2
  exit 2
fi

case "$1" in
  upgrade)
    action=upgrade
    revision=${2:-head}
    ;;
  rollback)
    action=downgrade
    revision=${2:-base}
    ;;
  *)
    echo "Usage: $0 upgrade [revision] | rollback [revision]" >&2
    exit 2
    ;;
esac

DB001_DATABASE_URL="$database_url" \
  "$alembic_bin" -c "$repo_root/backend/app/db/alembic.ini" "$action" "$revision"
