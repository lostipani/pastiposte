FROM python:3.12-slim

COPY ./requirements.txt /
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

WORKDIR /app
COPY __init__.py /app
COPY commons /app/commons
COPY analyst /app/analyst

CMD ["python", "-m", "analyst.analyst"]