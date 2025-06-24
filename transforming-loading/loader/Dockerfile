FROM python:3.10-bullseye
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    sudo \
    curl \
    vim \
    unzip \
    rsync \
    openjdk-11-jdk \
    build-essential \
    software-properties-common \
    ssh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*do

COPY ./requirements.txt /
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
RUN pip install pyspark

ARG SPARK_VERSION=3.5.5
ENV SPARK_HOME="/opt/spark"
ENV HADOOP_HOME="/opt/hadoop"
ENV JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64/"
ENV PATH="/opt/spark/sbin:/opt/spark/bin:${PATH}"
ENV PYSPARK_PYTHON python3
ENV PYTHONPATH=$SPARK_HOME/python/:$PYTHONPATH

WORKDIR /app
COPY __init__.py /app
COPY commons /app/commons
COPY transforming-loading/loader /app/loader

CMD ["python", "-m", "loader.loader"]
