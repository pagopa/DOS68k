from typing import Self, Any, Dict
from boto3 import client


class Boto3ClientMock:
    def __init__(self: Self, *args, **kwargs) -> None:
        pass

    def get_queue_url(self: Self, QueueName: str) -> Dict[str, str]:
        return {"QueueUrl": "http://mocked-queue-url"}

    def send_message(self: Self, QueueUrl: str, MessageBody: str, MessageGroupId: str, MessageDeduplicationId: str) -> Dict[str, str]:
        return {"MessageId": "mocked-message-id"}

    def receive_message(self: Self, QueueUrl: str, MaxNumberOfMessages: int, WaitTimeSeconds: int) -> Dict[str, Any]:
        return {"Messages": []}

    def delete_message(self: Self, QueueUrl: str, ReceiptHandle: str) -> None:
        return None

class Boto3ClientUnhealthyMock(Boto3ClientMock):
    def get_queue_url(self: Self, QueueName: str) -> Dict[str, str]:
        raise Exception("Simulated SQS client failure")

class Boto3ClientNewMessageDequeueMock(Boto3ClientMock):
    def receive_message(self: Self, QueueUrl: str, MaxNumberOfMessages: int, WaitTimeSeconds: int) -> Dict[str, Any]:
        return {
            "Messages": [
                {
                    "Body": "dGVzdC1tZXNzYWdl",  # base64 for "test-message"
                    "ReceiptHandle": "mocked-receipt-handle",
                }
            ]
        }

def boto3_client_mock(*args, **kwargs) -> Boto3ClientMock:
    return Boto3ClientMock()

def boto3_client_unhealthy_mock(*args, **kwargs) -> Boto3ClientUnhealthyMock:
    return Boto3ClientUnhealthyMock()

def boto3_client_new_message_dequeue_mock(*args, **kwargs) -> Boto3ClientNewMessageDequeueMock:
    return Boto3ClientNewMessageDequeueMock()