import discord
from discord.ext import commands
from dateutil.relativedelta import relativedelta
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)
MOD_LOG_CHANNEL_ID = 1560509074091802744
MOD_CHAT_CHANNEL_ID = 1560509069821743157
TOKEN = os.environ["DISCORD_TOKEN"]

@bot.command()
async def watchlist(ctx, y: int = 1, m: int = 0, d: int = 0, h: int = 0):
    wlist = []
    duration = relativedelta(years=y, months=m, days=d, hours=h)
    cutoff = datetime.now(timezone.utc) - duration
    async for member in ctx.guild.fetch_members(limit=None):
        if member.created_at > cutoff and member != bot.user:
            wlist.append(member.id)
    if ctx.channel.id != MOD_LOG_CHANNEL_ID and ctx.channel.id != MOD_CHAT_CHANNEL_ID:
        return
    else:
        # Good to run
        message = "## Watchlist\n"
        for i, userid in enumerate(wlist):
            message += f"{i+1}. <@{userid}>\n"

        await ctx.send(message)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Registered commands:", [cmd.name for cmd in bot.commands])

@bot.event
async def on_message(message):
    print(f"Received: {message.content!r}")

    ctx = await bot.get_context(message)

    print(f"Prefix: {ctx.prefix}")
    print(f"Command: {ctx.command}")
    print(f"Valid: {ctx.valid}")

    await bot.process_commands(message)

bot.run(TOKEN)
