import os
from datetime import datetime
from discord.ext import tasks, commands
from dotenv import load_dotenv
import pytz
import requests
import random

# 채널 정보를 환경 변수에서 세팅
target_channel = os.getenv('DISCORD_REMIND_CHANNEL')


# Cog 클래스
class Remind(commands.Cog):
    # 생성자, 봇을 받아 초기화함.
    def __init__(self, bot):
        self.bot = bot
        self.channels = [target_channel]  # 채널 ID 리스트로 변경

    # 반복 작업 구문
    @tasks.loop(minutes=60)  # 매 1시간 마다 반복.
    async def send_messages_to_channels(self):
        # 날짜 체크.
        KST = pytz.timezone('Asia/Seoul')
        dt = datetime.now().astimezone(KST)

        # 오전 9시 ~ 오후 9시 사이에만 실행한다.
        print(f'현재 시간 : {dt} -> {dt.hour} : {dt.minute} : {dt.second}')
        if (dt.hour == 9 and dt.minute >= 0 and dt.second >= 0) and (
                dt.hour < 22 and dt.minute <= 59 and dt.second <= 59):

            for channel_id in self.channels:
                try:
                    # 채널에 메세지를 전송한다.
                    channel = self.bot.get_channel(channel_id)
                    await channel.send(make_message(get_notion_data()))
                except Exception as e:
                    print(f"채널 ID {channel_id}를 찾을 수 없습니다.")
                    print(e)
        else:
            print('Remind 시간이 아닙니다.')

    # 작업 실행 전, 봇 실행이 완료될 때 까지 기다린다.
    @send_messages_to_channels.before_loop
    async def before_send_messages_to_channels(self):
        await self.bot.wait_until_ready()

    # Cog Listener, 준비가 완료되면 작업을 시작한다.
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} has connected to Discord!')
        self.send_messages_to_channels.start()

    def cog_unload(self):
        self.send_messages_to_channels.cancel()


# Cog 셋업 함수
async def setup(app):
    await app.add_cog(Remind(app))


# 데이터 -> 메세지 세팅 함수
def make_message(row):
    message = '**# ' + row['subject'] + '**'
    message += '\n>>> ' + row['info'] + '\n\n'
    print(message)
    return message


# 데이터를 노션에서 가져오는 함수
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
