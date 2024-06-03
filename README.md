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

### A propos des tests et des bases de données

Les tests sont destructifs: ils écrivent dans les bases de données, et détruisent
tout à la fin. Normalement, ils doivent se faire sur des bases de données dédiées
à cet usage (cf. conftest.py, des fixtures créent des bases de données, gèrent les
upgrades, et font les drops à la fin des tests). Si un test est mal écrit (s'il ne
passe pas par la bonne fixture), il aura lieu en se connectant à la base de données
par défaut (celle qui est configurée dans 'config/settings.toml'). C'est pourquoi:
- le fichier config/settings.toml contient des URL vers les bases de données qui ne
  permettent pas de se connecte (le mot de passe n'est pas le bon)
- les bonnes URLs, pour les bases qui tournent dans le mariadb du docker compose,
  doivent être dans un fichier '.env-dev' (utilisé par 'start-dev.sh'), pour être
  utilisées par uvicorn
- les fixtures de test produisent des URLs valides sur les bases qu'elles créent

Et donc, si un test est mal écrit (sans utiliser les bonnes fixtures) il va échouer
avec un message d'erreur explicite.

Si on met directement les bonnes URLs dans 'config/settings.toml', ou si on charge
le fichier '.env-dev' dans le terminal où on fait tourner 'pytest', alors un test
mal écrit va se connecter à la base du docker (et non à la base de test) et risque
de tout détruire à cet endroit là.

### Le script start-dev.sh

Ce script se charge de lancer toute l'application dans un environnement correct, à savoir :
- détecter si vous utilisez podman ou docker
- lancer le docker composer up (ou équivalent), ce qui va...
  - lancer un serveur mariadb dans un conteneur
  - lancer un serveur open-xchange dans un conteneur
- lancer uvicorn avec les bonnes options

Le script va chercher à la racine du dépôt un fichier '.env-dev' qui contient les variables
d'environnement utiles pour se connecter (en particulier, il contient les URL de connexions
aux bases de données, ainsi que le secret pour les JWT).

Exemple d'un fichier '.env-dev':

```bash
export DIMAIL_JWT_SECRET="Not the default secret"
export DIMAIL_API_DB_URL="mysql+pymysql://api_user:coincoin@localhost:3306/api"
export DIMAIL_IMAP_DB_URL="mysql+pymysql://dovecot:toto@localhost:3306/dovecot"
export DIMAIL_POSTFIX_DB_URL="mysql+pymysql://postfix:toto@localhost:3306/dovecot"
```

### Démarrer mariadb et un serveur OX
```bash
docker compose up -d
```

### Configurer les bases de données _(depuis le répertoire `src`)_
```bash
alembic revision --autogenerate -m "<votre_message>" 

alembic upgrade head
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
