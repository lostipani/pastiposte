FROM python:3.12-slim

COPY build/listener/requirements.txt /
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY src/ /app/src
WORKDIR /app/src

CMD ["python", "-m", "interfaces.listener"]