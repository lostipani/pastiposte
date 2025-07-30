FROM python:3.12-slim
RUN apt-get -y update; apt-get -y install curl

COPY ./requirements.txt /
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

WORKDIR /app
COPY __init__.py /app
COPY commons /app/commons
COPY server /app/server

CMD ["python", "-m", "server.server"]