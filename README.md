# Provisioning API for openXchange

## Installation de l'environnement de dev

### Créer un environnement python, installer les dépendances
python3 -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt

### Basculer dans l'environnement python
source ./.venv/bin/activate

### En sortir (revenir à l'interpréteur python du système)
deactivate

## Les outils pour tester

### Démarrer mariadb et un serveur ox
docker compose up -d

### Se connecter à la base dovecot
mysql -u dovecot -ptoto -h localhost -P 3306 dovecot

### Se connecter à la base api
mysql -u api_user -pcoincoin -h localhost -P 3306 api

### Lancer le serveur d'application (il faut être dans le bon environnement python)
uvicorn src.main:app --reload

### Lancer les tests
pytest

## Installation de pre-commit

[Pre-commit](https://pre-commit.com/) permet de linter et formatter votre code avant chaque commit. Par défaut ici, il exécute :

- [black](https://github.com/psf/black) pour formatter automatiquement vos fichiers .py en conformité avec la PEP 8 (gestion des espaces, longueur des lignes, etc)
- [flake8](https://github.com/pycqa/flake8) pour soulever les "infractions" restantes (import non utilisés, etc)
- [isort](https://github.com/pycqa/isort) pour ordonner vos imports

Pour l'installer :

```bash
pre-commit install
```

Vous pouvez effectuer un premier passage sur tous les fichiers du repo avec :

```bash
pre-commit run --all-files
```
