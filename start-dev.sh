#!/usr/bin/env sh

dir=`/usr/bin/env dirname $0`
envfile="$dir/.env-dev"
if [ -f "$envfile" ]; then
  . $envfile
else
  echo "Je ne trouve pas de fichier $envfile, essayons sans..."
fi

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
    DOCKER=podman
  fi
fi

echo "container runtime -> ${DOCKER}"

wait_for_ox=1
if [ -n "$($DOCKER ps -f "name=oxtest" -f "status=running" -q )" ]; then
  echo "the ox container is running!"
  wait_for_ox=0
fi

wait_for_mariadb=1
if [ -n "$($DOCKER ps -f "name=mariadb" -f "status=running" -q )" ]; then
  echo "the mariadb container is running!"
  wait_for_mariadb=0
fi

if [ "$wait_for_ox$wait_for_mariadb" = "00" ]; then
  echo "Both containers ok."
else
  echo "Missing container, compose up..."
  $DOCKER compose up -d
  if [ $wait_for_ox = "1" ]; then
    sleep 25
  fi
fi

cd $dir
cd src/ || exit
alembic upgrade head
cd ..
uvicorn src.main:app --reload --log-level info
cd src/ || exit
# alembic downgrade head
cd ..
# $DOCKER compose down
