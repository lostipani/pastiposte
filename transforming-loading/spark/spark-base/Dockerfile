FROM bitnami/spark:3.5

WORKDIR /app
COPY __init__.py /app
COPY commons /app/commons
COPY loader /app/loader
RUN pip install --no-cache-dir --upgrade -r loader/requirements.txt

CMD ["python", "-m", "loader.loader"]