#!/bin/bash
set -e

awslocal dynamodb create-table \
    --table-name sessions \
    --key-schema AttributeName=userId,KeyType=HASH AttributeName=createdAt,KeyType=RANGE \
    --attribute-definitions AttributeName=userId,AttributeType=S AttributeName=createdAt,AttributeType=S \
    --billing-mode PAY_PER_REQUEST

awslocal dynamodb create-table \
    --table-name queries \
    --key-schema AttributeName=sessionId,KeyType=HASH AttributeName=createdAt,KeyType=RANGE \
    --attribute-definitions AttributeName=sessionId,AttributeType=S AttributeName=createdAt,AttributeType=S \
    --billing-mode PAY_PER_REQUEST
