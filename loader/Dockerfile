FROM python:3.12-slim

COPY ./requirements.txt /
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

WORKDIR /app
COPY __init__.py /app
COPY commons /app/commons
<<<<<<<< HEAD:consumer/Dockerfile
COPY consumer /app/consumer

CMD ["python", "-m", "consumer.consumer"]
========
COPY client_multiprocess/loader /app/loader

CMD ["python", "-m", "loader.loader"]
>>>>>>>> cfb9b1b (add seq diagram; removed other profiles in docker-compose; add some LLM):client_multiprocess/loader/Dockerfile
