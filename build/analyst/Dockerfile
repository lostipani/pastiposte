FROM python:3.12-slim

COPY build/analyst/requirements.txt /
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY src/ /app/src
WORKDIR /app/src

CMD ["python", "-m", "analyst.analyst"]