import os
from datetime import datetime
from discord.ext import tasks, commands
from dotenv import load_dotenv
import pytz
import requests
import random
import ast
# postgres
import psycopg2

# 채널 정보를 환경 변수에서 세팅 (스트링 배열 -> int 배열)
target_channel = ast.literal_eval(os.getenv('DISCORD_REMIND_CHANNEL'))

# 가져온 데이터 아이디 값 저장, 여기에 저장된 친구들은 초기화되기 전까지 다시 안가져옴.
used_data_keys = []

# send condition
is_time_ok = False
is_test = False

# postgres conn variable
conn = None


# Cog 클래스
class Remind(commands.Cog):
    # 생성자, 봇을 받아 초기화함.
    def __init__(self, bot):
        self.bot = bot
        self.channels = target_channel  # 채널 ID 리스트로 변경

    # 반복 작업 구문
    @tasks.loop(hours=24)  # 매 24시간 마다 반복.
    async def clear_used_data(self):
        used_data_keys = []

    # 반복 작업 구문
    @tasks.loop(minutes=59)  # 매 1시간 마다 반복.
    async def send_messages_to_channels(self):
        # 날짜 체크.
        KST = pytz.timezone('Asia/Seoul')
        dt = datetime.now().astimezone(KST)
        is_time_ok = (dt.hour >= 9 and dt.minute >= 0 and dt.second >= 0) and (
                dt.hour < 22 and dt.minute <= 59 and dt.second <= 59)

        # 오전 9시 ~ 오후 9시 사이에만 실행한다.
        # print(f'현재 시간 : {dt} -> {dt.hour} : {dt.minute} : {dt.second}')
        # print(f'send condition -> time: {is_time_ok} and test: {is_test}')
        if is_time_ok and not is_test:
            for channel_id in self.channels:
                try:
                    # 채널에 메세지를 전송한다.
                    channel = self.bot.get_channel(channel_id)
                    # await channel.send(make_message(get_notion_data())) notion
                    await channel.send(make_message(get_postgres_data()))  # postgres in home
                except Exception as e:
                    print(e)

    # 작업 실행 전, 봇 실행이 완료될 때 까지 기다린다.
    @send_messages_to_channels.before_loop
    async def before_send_messages_to_channels(self):
        # print(f'{self.bot.user} await before send!')
        await self.bot.wait_until_ready()

    # Cog Listener, 준비가 완료되면 작업을 시작한다.
    @commands.Cog.listener()
    async def on_ready(self):
        # print(f'{self.bot.user} has connected to Discord!')
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


def get_postgres_data():
    try:
        host = os.getenv('POSTGRES_HOST')
        dbname = os.getenv('POSTGRES_DB')
        user = os.getenv('POSTGRES_ID')
        password = os.getenv('POSTGRES_PASS')
        port = os.getenv('POSTGRES_PORT')

        conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
        cursor = conn.cursor()

        # 체크 로직에 의한 무한반복
        while True:
            # 랜덤으로 하나 가져오기!
            sql = "select * from remind_contents order by random() limit 1"
            cursor.execute(sql)
            result = cursor.fetchone()

            # 결과가 있는지 확인 후 출력
            if result is not None:
                # 인덱스를 이용하여 각 항목 선택
                content_id = result[0]
                title = result[1]
                contents = result[2]
            else:
                # print("결과가 없습니다.")
                break

            # 결과가 이전에 사용됨. -> 다시 가져오기.
            # print(f"this id [{content_id}] is Used!")
            if content_id not in used_data_keys:
                # 결과가 이전에 사용되지 않음 -> 기록하고, 그대로 보내기
                used_data_keys.append(content_id)
                # 해당 데이터를 파싱하여 리턴.
                data = {'subject': title, 'info': contents}
                return data
            # 이전에 가져온 데이터 인지 체크!
    except Exception as e:
        print("get_postgres_data error : ", e)


load_dotenv()
