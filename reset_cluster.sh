#!/bin/bash

if [ -f kafka/kafka-logs-*/meta.properties]; then
    echo "Removing meta.properties.."
    rm -f kafka/kafka-logs-*/meta.properties

fi 

echo "Starting Kafka"
exec start-kafka.sh