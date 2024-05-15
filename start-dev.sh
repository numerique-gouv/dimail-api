#!/bin/bash

# vérifie que python est bien activé
if ! command -v alembic > /dev/null 2>&1 || ! command -v uvicorn > /dev/null 2>&1; then
  echo "l'environnement python n'est pas configuré ou est désactivé (voir le README)"
  exit 1
fi

# défini le runtime de container
DOCKER=docker
if command -v podman > /dev/null 2>&1; then
  # Vérifie si la commande docker est disponible et fonctionne
  if ! command -v docker > /dev/null 2>&1 || ! docker ps > /dev/null 2>&1; then
    echo "podman sera utilisé à la place de docker"
    DOCKER=podman
  fi
fi

$DOCKER compose up -d
sleep 25
cd src/ || exit
alembic upgrade head
cd ..
uvicorn src.main:app --reload --log-level info
cd src/ || exit
# alembic downgrade head
cd ..
# $DOCKER compose down