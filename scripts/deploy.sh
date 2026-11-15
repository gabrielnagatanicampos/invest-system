#!/usr/bin/env bash
# Publica/atualiza o Invest System na VPS. Pode rodar várias vezes.
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker não encontrado. Instalando..."
  curl -fsSL https://get.docker.com | sudo sh
  sudo usermod -aG docker "$USER" || true
fi

DC="docker compose"
if ! docker info >/dev/null 2>&1; then DC="sudo docker compose"; fi

if [ ! -f .env ]; then
  echo "Arquivo .env não encontrado. Copie .env.example para .env e preencha." >&2
  exit 1
fi

git pull --ff-only

# Com DOMINIO definido, liga o Caddy (HTTPS) e fecha a 8501 para fora.
DOMINIO="$(grep -E '^DOMINIO=' .env | head -n1 | cut -d= -f2- | tr -d '"' || true)"
if [ -n "$DOMINIO" ]; then
  export COMPOSE_PROFILES=https APP_BIND=127.0.0.1
  echo "Modo HTTPS para $DOMINIO"
else
  echo "Sem DOMINIO: app publicado na porta 8501"
fi

$DC up -d --build
$DC ps
