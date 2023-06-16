import asyncio
import functools
import uvicorn
from loguru import logger

from app import app
from khl_bot import bot, send_notify
from twitter_playwright import check_notify, LAST_NOTIFY_TIME

logger.add("logs/{time}.log", rotation="1 day", retention="7 days")


async def check_task():
    while True:
        try:
            logger.info("check_task")
            tweet = await check_notify()

            if tweet:
                await send_notify(tweet)
                LAST_NOTIFY_TIME.time = tweet.post_time
        except Exception as e:
            logger.exception(e)

        await asyncio.sleep(60)


async def main():
    loop = asyncio.get_event_loop()

    coro = [check_task(), bot.start(), loop.run_in_executor(
        None, functools.partial(uvicorn.run, app, host="0.0.0.0", port=3000))]

    await asyncio.gather(*coro, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())
