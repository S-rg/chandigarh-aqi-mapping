#!/bin/bash

REPO_DIR="/Desktop/chandigarh-aqi-mapping"
DEPLOY_DIR="/var/www/flaskapp"

cd "$REPO_DIR" || exit
git pull origin main

rsync -av --delete "$REPO_DIR/webapp/" "$DEPLOY_DIR/"
