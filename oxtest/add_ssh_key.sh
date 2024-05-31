#!/bin/sh


# Récupérer le répertoire où se trouve le script
dir="$(dirname $0)"

# Générer une clé SSH sans mot de passe
ssh-keygen -t rsa -b 4096 -q -N "" \
  -f /tmp/id_rsa \
  -C "tu@dimail" \


# Ajouter la clé privée SSH à l'agent SSH
#eval "$(ssh-agent -s)"
ssh-add /tmp/id_rsa

# Copier la clé publique SSH dans le fichier authorized-keys
echo "$(cat /tmp/id_rsa.pub)" >> "${dir}/authorized_keys"

# Afficher un message de confirmation
echo "Clé SSH générée, clé privée ajoutée à l'agent SSH et clé publique copiée dans authorized-keys"