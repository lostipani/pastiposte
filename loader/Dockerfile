FROM bitnami/spark:3.5
RUN pip install --no-cache-dir --upgrade pika==1.3.2 \
    pyspark[sql,pandas_on_spark]==3.5.0 \
    grpcio \
    protobuf \
    grpcio-status

WORKDIR /app
COPY __init__.py /app
COPY commons /app/commons
COPY loader /app/loader

CMD ["python", "-m", "loader.loader"]