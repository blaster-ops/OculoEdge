#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
if [ -x .venv/bin/python ]; then
  exec .venv/bin/python run.py "$@"
fi
printf '%s\n' 'Cree .venv e instale requirements-lock.txt antes de ejecutar.'
exit 1
