#!/bin/bash
set -e  # stop if any command fails

echo "Killing and deleting all containers"
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)

echo "Deleting all persistent volumes"
docker volume rm $(docker volume ls -q)

echo "Building containers and upping them"
docker compose --project-directory deploy --profile real-world up --build

