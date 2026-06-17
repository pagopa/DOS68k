#!/bin/bash
set -e

awslocal dynamodb create-table \
    --table-name sessions \
    --key-schema AttributeName=userId,KeyType=HASH AttributeName=id,KeyType=RANGE \
    --attribute-definitions AttributeName=userId,AttributeType=S AttributeName=id,AttributeType=S \
    --billing-mode PAY_PER_REQUEST

awslocal dynamodb update-time-to-live \
    --table-name sessions \
    --time-to-live-specification "Enabled=true,AttributeName=expiresAt"

awslocal dynamodb create-table \
    --table-name queries \
    --key-schema AttributeName=sessionId,KeyType=HASH AttributeName=id,KeyType=RANGE \
    --attribute-definitions AttributeName=sessionId,AttributeType=S AttributeName=id,AttributeType=S \
    --billing-mode PAY_PER_REQUEST

awslocal dynamodb update-time-to-live \
    --table-name queries \
    --time-to-live-specification "Enabled=true,AttributeName=expiresAt"
