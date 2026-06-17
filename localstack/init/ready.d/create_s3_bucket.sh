#!/bin/bash
set -e

awslocal s3api create-bucket --bucket sample-bucket
awslocal s3api create-bucket --bucket langfuse # For Langfuse