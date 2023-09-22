import os
import datetime
from discord.ext import tasks, commands
from dotenv import load_dotenv
import requests
import random

target_channel = os.getenv('DISCORD_REMIND_CHANNEL')


class Remind(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channels = [target_channel]  # 채널 ID 리스트로 변경

    @tasks.loop(minutes=60)  # 매 1시간 마다 반복.
    async def send_messages_to_channels(self):
        # 날짜 체크.
        dt = datetime.datetime.now()

        # 오전 9시 ~ 오후 9시 사이에만 실행한다.
        print(f'현재 시간 : {dt}')
        if (dt.hour == 9 and dt.minute >= 0 and dt.second >= 0) and (
                dt.hour < 22 and dt.minute <= 59 and dt.second <= 59):

            for channel_id in self.channels:
                try:
                    channel = self.bot.get_channel(channel_id)
                    await channel.send(make_message(get_notion_data()))
                except Exception as e:
                    print(f"채널 ID {channel_id}를 찾을 수 없습니다.")
                    print(e)
        else:
            print('Remind 시간이 아닙니다.')

    @send_messages_to_channels.before_loop
    async def before_send_messages_to_channels(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} has connected to Discord!')
        self.send_messages_to_channels.start()

    def cog_unload(self):
        self.send_messages_to_channels.cancel()


async def setup(app):
    await app.add_cog(Remind(app))


def make_message(row):
    message = '**# ' + row['subject'] + '**'
    message += '\n>>> ' + row['info'] + '\n\n'
    print(message)
    return message


def get_notion_data():
    t = os.getenv('NOTION_CONNECTION_TOKEN')
    b = "https://api.notion.com/v1/databases/"
    d = os.getenv('NOTION_DB_ID')
    header = {"Authorization": t, "Notion-Version": "2022-06-28"}

    response = requests.post(b + d + "/query", headers=header, data="")

    # 데이터베이스 내용 중 랜덤으로 하나 뽑기.
    choice = random.choice(response.json()["results"])
    # 해당 데이터를 파싱하여 리턴.
    data = {'subject': choice["properties"]["subject"]["title"][0]["text"]["content"],
            'info': choice["properties"]["info"]["rich_text"][0]["text"]["content"]}

    return data


load_dotenv()
