import asyncio
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

# 환경 변수 로딩
load_dotenv()

# 디스코드 봇 토큰 값 지정
token = os.getenv('DISCORD_BOT_TOKEN')

# 디스코드 봇 인텐트 및 봇 초기화
intents = discord.Intents.all()
bot = commands.Bot(intents=intents, command_prefix='!')


# Cogs 모듈 로딩을 위한 구문, 파일을 통해 구분하여 가져옴
# 이렇게 하면, 폴더 내부에 모듈 넣어서 관리할 수 있어 편함.
async def load_extensions():
    for filename in os.listdir("Cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"Cogs.{filename[:-3]}")


# 메인 함수 호출
# 디스코드 특정 버전(12++) 부터 async를 적용해야 제대로 호출이 가능함.
async def main():
    async with bot:
        await load_extensions()
        await bot.start(token)


# asyncio를 통해 봇 구동.
asyncio.run(main())
