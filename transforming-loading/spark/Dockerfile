# set up O/S
FROM python:3.12-bullseye as spark-base
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
COPY transforming-loading/spark/requirements.txt .
RUN pip3 install -r requirements.txt

# set fundamental variables
ARG SPARK_VERSION=3.5.5
ENV SPARK_HOME=${SPARK_HOME:-"/opt/spark"}
ENV HADOOP_HOME=${HADOOP_HOME:-"/opt/hadoop"}
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64/
ENV PATH="/opt/spark/sbin:/opt/spark/bin:${PATH}"
ENV SPARK_MASTER="spark://spark-master:7077"
ENV SPARK_MASTER_HOST spark-master
ENV SPARK_MASTER_PORT 7077
ENV PYSPARK_PYTHON python3
ENV PYTHONPATH=$SPARK_HOME/python/:$PYTHONPATH

# set up spark
RUN mkdir -p ${HADOOP_HOME} && mkdir -p ${SPARK_HOME}
WORKDIR ${SPARK_HOME}
RUN wget https://archive.apache.org/dist/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop3.tgz \
    && tar xvzf spark-$SPARK_VERSION-bin-hadoop3.tgz --directory /opt/spark \
    --strip-components 1 && rm -rf spark-$SPARK_VERSION-bin-hadoop3.tgz
FROM spark-base as pyspark

# config spark
COPY transforming-loading/spark/spark-defaults.conf "$SPARK_HOME/conf"
RUN chmod u+x /opt/spark/sbin/* && \
    chmod u+x /opt/spark/bin/*

# set up entrypoint of container
COPY transforming-loading/spark/entrypoint.sh .
RUN chmod 777 ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
