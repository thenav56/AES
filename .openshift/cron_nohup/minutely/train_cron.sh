#!/bin/bash

echo "************ Cronny Started ( NoHup ) ***************"

python ${OPENSHIFT_REPO_DIR}wsgi/myproject/cron.py

echo "************ Cronny Executed ( NoHup ) ***************"
