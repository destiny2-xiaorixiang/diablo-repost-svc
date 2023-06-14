import asyncio
import datetime
from khl import Bot, Message
from khl.card import Card, CardMessage, Element, Module, Types

from config import BOT_TOKEN, CHANNEL_IDS
from twitter_playwright import TweetModel

bot = Bot(token=BOT_TOKEN)


@bot.command("hello")
async def test(message: Message):
    await message.reply("hello")


async def send_notify(tweet: TweetModel):
    urls = await asyncio.gather(*[bot.client.create_asset(image) for image in tweet.imgs.values()])

    card = Card(theme=Types.Theme.NONE, size=Types.Size.SM)
    divider = Module.Divider()

    head = Module.Section(
        Element.Text(
            "(met)1503437691(met) **世界首领** 已出现！"
        )
    )

    sections = []
    if tweet.boss:
        for name, value in zip(["💀 Boss", "🚩 刷新位置"], [tweet.boss, tweet.location]):
            sections.append(Module.Section(
                Element.Text(f"**{name}**：`{value}`")))
        sections.append(Module.Section(
            Element.Text("**⏰ 距离活动开始还剩：**")))
        sections.append(Module.Countdown(
            tweet.post_time + datetime.timedelta(minutes=tweet.minutes),
            mode=Types.CountdownMode.HOUR,
        ))
        sections.append(Module.ImageGroup(
            *[Element.Image(url) for url in urls]))
    else:
        sections.append(Module.Section(
            Element.Text(tweet.text)))

    bottom = Module.Context(
        Element.Text(
            "小日向 | 暗黑4世界首领Bot"
        )
    )

    card._modules = [head, divider, *sections, divider, bottom]

    for channel_id in CHANNEL_IDS:
        channel = await bot.fetch_public_channel(channel_id)
        await channel.send(CardMessage(card))
