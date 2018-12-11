#!/usr/bin/env bash

source ./venv/bin/activate
source ./private-env.sh

export FLASK_APP=api-server.py
export FLASK_ENV=development

echo Serving $FLASK_APP in $FLASK_ENV mode
flask run
