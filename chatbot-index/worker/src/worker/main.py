import asyncio
import logging

from dos_utility.queue.redis import get_queue_client_ctx

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def main():
    async with get_queue_client_ctx() as queue_client:
        while True:
            logging.info("Worker started and connected to the queue.")
            logging.info("Waiting for tasks...")

            break #! Handle for tests, if needed remove it for production


if __name__ == "__main__":
    asyncio.run(main())
