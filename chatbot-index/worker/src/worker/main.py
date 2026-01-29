import asyncio
import logging

from dos_utility.queue import get_queue_client_ctx

from .task import process_task

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def main():
    async with get_queue_client_ctx() as queue_client:
        logging.info("Worker started and connected to the queue.")
        logging.info("Waiting for tasks...")

        while True:
            msg, ack_token = await queue_client.dequeue()

            if msg is not None:
                await process_task(body=msg)

                if ack_token is not None:
                    await queue_client.acknowledge(ack_token=ack_token)


if __name__ == "__main__":
    asyncio.run(main())
