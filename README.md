# Provisioning API for openXchange

## Installation de l'environnement de dev

### Créer un environnement python, installer les dépendances
```bash
python3 -m venv .venv
source venv/bin/activate
pip install -r requirements.txt
```

### Basculer dans l'environnement python
```bash
source venv/bin/activate
```

### En sortir (revenir à l'interpréteur python du système)
```bash
deactivate
```

## Les outils pour tester

### Démarrer mariadb et un serveur OX
```bash
docker compose up -d
```

### Configurer les bases de données _(depuis le répertoire `src`)_
```bash
alembic revision --autogenerate -m "<votre_message>" 

alembic upgrade head
```

### Modifier les URLs vers vos bases de données 

Dynaconf recupère par défaut les URLs dans `config/settings.toml`. Vous pouvez surcharger ces valeurs en exportant `DIMAIL_API_DB_URL`, `DIMAIL_DOVECOT_DB_URL`, et `DIMAIL_POSTFIX_DB_URL`
dans le terminal dans lequel vous lancer uvicorn. 

```
Attention à ne pas lancer pytest dans le même terminal, les tests risqueraient de tourner sur vos bases de données et d'altérer/supprimer leurs contenus.
```

### Se connecter à la base dovecot
```bash
mysql -u dovecot -ptoto -h localhost -P 3306 dovecot
```

### Se connecter à la base api
```bash
mysql -u api_user -pcoincoin -h localhost -P 3306 api
```

### Lancer le serveur d'application (il faut être dans le bon environnement python)
```bash
uvicorn src.main:app --reload
```

Pour que uvicorn affiche tous les logs (et pas seulement les siens) :
```bash
uvicorn src.main:app --reload --log-config logs.yaml
```

### Lancer les tests _(depuis le répertoire `src`)_

Pour lancer tout le pipeline :
```bash 
pytest
```

Pour lancer un test en partculier :
```
pytest -k <votre_test> 
```


### Installation de pre-commit

[Pre-commit](https://pre-commit.com/) permet de linter et formatter votre code avant chaque commit. Un code linté selon les mêmes règles est plus simple à comprendre. Par défaut ici, il exécute :

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
