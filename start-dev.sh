if command -v docker &> /dev/null; then DOCKER=docker; else DOCKER=podman;fi

$DOCKER compose up -d
sleep 25
cd src/
alembic upgrade head
cd ..
uvicorn src.main:app --reload
cd src/
alembic downgrade head
cd ..
$DOCKER compose down