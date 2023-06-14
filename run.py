import asyncio
import datetime
import functools

import uvicorn
from app import app
from khl_bot import bot, send_notify
from twitter_playwright import check_notify, LAST_NOTIFY_TIME


async def check_task():
    while True:
        try:
            print(datetime.datetime.now(), "check")
            tweet = await check_notify()

            if tweet:
                await send_notify(tweet)
                LAST_NOTIFY_TIME.time = tweet.post_time
        except Exception as e:
            print(datetime.datetime.now(), e)

        await asyncio.sleep(60)


async def main():
    loop = asyncio.get_event_loop()

    coro = [check_task(), bot.start(), loop.run_in_executor(
        None, functools.partial(uvicorn.run, app, host="0.0.0.0", port=3000))]

    await asyncio.gather(*coro, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())
