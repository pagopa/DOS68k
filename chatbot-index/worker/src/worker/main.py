import asyncio
import traceback

from logging import Logger
from task import process_task
from dos_utility.queue import get_queue_client_ctx
from dos_utility.utils.logger import get_logger

from env import get_global_settings, GlobalSettings


async def main():
    settings: GlobalSettings = get_global_settings()
    logger: Logger = get_logger(name=__file__, level=settings.log_level)

    async with get_queue_client_ctx() as queue_client:
        logger.info("Worker started and connected to the queue.")
        logger.info("Waiting for tasks...")

        while True:
            try:
                msg, ack_token = await queue_client.dequeue()

                if msg is not None:
                    logger.info("Task found. Start processing..")
                    await process_task(body=msg)

                    if ack_token is not None:
                        await queue_client.acknowledge(ack_token=ack_token)
            except Exception:
                traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
