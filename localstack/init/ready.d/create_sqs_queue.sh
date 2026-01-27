#!/bin/bash
set -e

awslocal sqs create-queue --queue-name my-queue.fifo --attributes FifoQueue=true
