import asyncio

from logging import Logger
from dos_utility.queue import get_queue_client_ctx
from dos_utility.utils.logger import get_logger

from task import process_task
from env import get_global_settings, GlobalSettings


async def main():
    settings: GlobalSettings = get_global_settings()
    logger: Logger = get_logger(name=__name__, level=settings.log_level)

    async with get_queue_client_ctx() as queue_client:
        logger.info("Worker started and connected to the queue.")
        logger.info("Waiting for tasks...")

        while True:
            try:
                msg, ack_token = await queue_client.dequeue()

                if msg is not None:
                    logger.info("Task found. Start processing...")
                    logger.debug(f"Message content: {msg}")

                    await process_task(body=msg)

                    logger.info("Task correctly processed")

                    if ack_token is not None:
                        await queue_client.acknowledge(ack_token=ack_token)
                        logger.debug("Message acknowledged and removed from queue")
                    else:
                        logger.warning(
                            "No ack token received - message may not be removed from queue"
                        )
            except Exception as e:
                logger.error(f"Error processing task: {str(e)}", exc_info=True)


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(main())
