#!/bin/bash

REPO_DIR="."
DEPLOY_DIR="/var/www/flaskapp"

cd "$REPO_DIR" || exit
git fetch origin main
git reset --hard origin/main

sudo chmod +x ./update-webpage.sh

rsync -av --delete --exclude='.env' "$REPO_DIR/webapp/" "$DEPLOY_DIR/"

sudo systemctl restart apache2