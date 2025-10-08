#!/bin/bash
set -e  # stop if any command fails

echo "Deleting all containers"
docker rm $(docker ps -aq)

echo "Deleting all persistent volumes"
docker volume rm $(docker volume ls -q)

echo "Building containers and upping them"
docker compose --project-directory deploy --profile real-world up --build

