FROM confluentinc/cp-server-connect-base:7.9.1

# Based on
# https://docs.confluent.io/platform/current/installation/docker/development.html#extending-images

# Execute manually
# git clone https://github.com/confluentinc/kafka-connect-jdbc.git
# cd kafka-connect-jdbc && \
# git checkout v10.7.0 && \
# git checkout -b geometry-support-based-on-10.7.0 && \
# git apply ../postgis-support.patch && \
# mvn clean package -DskipTests -Dcheckstyle.skip=true && \


# Create package structure:
# mkdir kafka-connect-jdbc-10.7.0
# mkdir kafka-connect-jdbc-10.7.0/assets
# mkdir kafka-connect-jdbc-10.7.0/lib
# mkdir kafka-connect-jdbc-10.7.0/etc
# mkdir kafka-connect-jdbc-10.7.0/doc
# cp target/manifest.json kafka-connect-jdbc-10.7.0
# cp target/kafka-connect-jdbc-10.7.0.jar kafka-connect-jdbc-10.7.0/lib
# cp target/kafka-connect-jdbc-10.7.0-package/etc/kafka-connect-jdbc/* kafka-connect-jdbc-10.7.0/etc/
# zip -r kafka-connect-jdbc-10.7.0.zip kafka-connect-jdbc-10.7.0

COPY ./kafka-connect-jdbc/kafka-connect-jdbc-10.7.0.zip /tmp/kafka-connect-jdbc-10.7.0.zip

RUN confluent-hub install --no-prompt mongodb/kafka-connect-mongodb:1.16.0 && \
    #confluent-hub install --no-prompt confluentinc/kafka-connect-jdbc:10.8.4 && \
    confluent-hub install --no-prompt /tmp/kafka-connect-jdbc-10.7.0.zip

