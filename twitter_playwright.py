import asyncio
import re
import datetime
from pydantic import BaseModel
from bs4 import BeautifulSoup
from bs4.element import Tag
from playwright.async_api import async_playwright, Browser, Page, Response, Request

from config import BOSS_KW_DICT, LOC_KW_DICT


BEIJING_TIMEZONE = datetime.timezone(datetime.timedelta(hours=8))
BOSS_REGEX = re.compile(
    "(.+)(?: spawning| spawn) in (.+) in (\d+) minutes", re.I)


class TweetModel(BaseModel):
    text: str
    boss: str | None
    location: str | None
    minutes: int | None
    imgs: dict[str, bytes] | None
    post_time: datetime.datetime


async def fetch_tweets(browser: Browser):
    tweets: list[TweetModel] = []
    imgs_dict: dict[str, str] = {}

    page: Page = await browser.new_page(viewport={'width': 2560, 'height': 1440})

    req_cnt = [0]

    async def on_request(req: Request):
        if req.resource_type == 'image':
            req_cnt[0] += 1

    async def on_response(resp: Response):
        if resp.request.resource_type == 'image':
            image_bytes = await resp.body()
            imgs_dict[resp.url] = image_bytes
            req_cnt[0] -= 1

    page.on('request', on_request)
    page.on('response', on_response)

    async def wait_for_img():
        while req_cnt[0] > 0:
            await asyncio.sleep(0.2)

    await page.goto("https://twitter.com/game8_d4boss")
    await page.wait_for_timeout(10000)
    await page.wait_for_selector("//div[@data-testid='cellInnerDiv']")
    await asyncio.wait_for(wait_for_img(), timeout=20)

    content = await page.content()

    soup = BeautifulSoup(content, "html.parser")
    divs: list[Tag] = soup.find_all(
        'div', attrs={"data-testid": "cellInnerDiv"})

    tweets: list[TweetModel] = []

    for div in divs:
        if not (time := div.find('time')):
            continue

        # 2023-06-12T04:46:51.000Z
        time_str = time.attrs['datetime']
        utc_time = datetime.datetime.strptime(
            time_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=datetime.timezone.utc)
        bj_time = utc_time.astimezone(BEIJING_TIMEZONE)

        spans: list[Tag] = div.find_all(
            attrs={"data-testid": "tweetText"})
        if not spans:
            continue

        imgs: list[Tag] = [img for img in div.find_all(
            'img') if img.attrs.get('alt')]
        text = "\n".join([span.text for span in spans])
        if 'spawn' not in text:
            continue

        data = {}

        if match := BOSS_REGEX.match(text):
            boss, location, minutes = match.groups()

            for k, v in BOSS_KW_DICT.items():
                if re.search(v, boss, re.I):
                    boss = k
                    break

            for k, v in LOC_KW_DICT.items():
                if re.search(v, location, re.I):
                    location = k
                    break

            data = {'boss': boss, 'location': location, 'minutes': minutes}

        img_urls = [img.attrs['src'] for img in imgs]
        tweet_model = TweetModel(
            text=text, imgs={k: imgs_dict[k] for k in img_urls}, post_time=bj_time, **data)
        tweets.append(tweet_model)

    return sorted(tweets, key=lambda tweet: tweet.post_time, reverse=True)


class LAST_NOTIFY_TIME:
    time = None


async def check_notify():
    async with async_playwright() as p:
        async with await p.firefox.launch() as browser:
            tweets = await fetch_tweets(browser)
            print("tweets len=", len(tweets))
            if not tweets:
                return

            tweet = tweets[0]
            local_time = datetime.datetime.now(BEIJING_TIMEZONE)

            # return tweet
            # 如果是程序第一次运行,且最新的提醒是5分钟内的,则发送
            if LAST_NOTIFY_TIME.time is None and local_time - tweet.post_time < datetime.timedelta(minutes=20):
                return tweet

            # 如果程序之前已经提醒过,出现了新的提醒
            if LAST_NOTIFY_TIME.time is not None and tweet.post_time > LAST_NOTIFY_TIME.time:
                return tweet
