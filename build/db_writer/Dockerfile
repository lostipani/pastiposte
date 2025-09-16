FROM python:3.12-slim

COPY build/db_writer/requirements.txt /
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY src/ /app/src
WORKDIR /app/src

CMD ["python", "-m", "db_writer.app"]
