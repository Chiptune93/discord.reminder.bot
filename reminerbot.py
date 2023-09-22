import asyncio
import os

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(intents=intents, command_prefix='!')


async def load_extensions():
    for filename in os.listdir("Cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"Cogs.{filename[:-3]}")


async def main():
    async with bot:
        await load_extensions()
        await bot.start(token)


asyncio.run(main())
