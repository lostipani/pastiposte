FROM python:3.12-slim
RUN apt-get -y update; apt-get -y install curl

COPY build/server/requirements.txt /
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY src/ /app/src
WORKDIR /app/src

CMD ["python", "-m", "server.server"]