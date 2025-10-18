#!/bin/bash
set -e  # stop if any command fails

#!/bin/bash
echo "Killing and deleting all containers"
if [ "$(docker ps -q)" ]; then
  docker stop $(docker ps -q)
fi

if [ "$(docker ps -aq)" ]; then
  docker rm $(docker ps -aq)
fi

echo "Deleting all persistent volumes"
if [ "$(docker volume ls -q)" ]; then
  docker volume rm $(docker volume ls -q)
fi

echo "Building containers and upping them"
docker compose --project-directory deploy --profile real-world up --build

