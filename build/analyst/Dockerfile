FROM python:3.12-slim

COPY build/analyst/requirements.txt /
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

WORKDIR /app
COPY src/ /app/src

CMD ["python", "-m", "analyst.analyst"]