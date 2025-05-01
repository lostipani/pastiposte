FROM openjdk:11-jdk-slim

# Set environment variables
ENV SPARK_VERSION=3.4.0
ENV HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Download and install Spark
RUN curl -sL "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" \
    | tar -xz -C /opt && \
    ln -s /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} ${SPARK_HOME}

# Copy configuration files
COPY spark-defaults.conf ${SPARK_HOME}/conf/

# Install PySpark (for Spark to use Python)
RUN pip3 install --upgrade pip && \
    pip3 install pyspark==${SPARK_VERSION}

# Expose Spark ports
EXPOSE 4040 7077 8080 8081

# Command to run Spark master
CMD ["sh", "-c", "${SPARK_HOME}/sbin/start-master.sh && ${SPARK_HOME}/sbin/start-worker.sh spark://$(hostname):7077 && tail -f ${SPARK_HOME}/logs/*"]
