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

bot = commands.Bot(command_prefix="?", intents=intents, help_command=None)
MOD_LOG_CHANNEL_ID = 1560509074091802744
MOD_CHAT_CHANNEL_ID = 1560509069821743157
THEN_WE_FIGHT_SERVER_ID = 1560467438154420295
TOKEN = os.environ["DISCORD_TOKEN"]
watchlist = {}
mod_log_channel_dict = {}
mod_log_channel_dict[THEN_WE_FIGHT_SERVER_ID] = MOD_LOG_CHANNEL_ID
whitelist = {}

@bot.command()
async def init(ctx, y: int = 1, m: int = 0, d: int = 0, h: int = 0):
    if ctx.channel.id != MOD_LOG_CHANNEL_ID and ctx.channel.id != MOD_CHAT_CHANNEL_ID:
        return 
    watchlist[ctx.guild.id] = []
    whitelist[ctx.guild.id] = []
    duration = relativedelta(years=y, months=m, days=d, hours=h)
    cutoff = datetime.now(timezone.utc) - duration
    async for member in ctx.guild.fetch_members(limit=None):
        if member.created_at > cutoff and member != bot.user and member not in watchlist[ctx.guild.id] and member not in whitelist[ctx.guild.id]:
            watchlist[ctx.guild.id].append(member)
    if len(watchlist[ctx.guild.id]) == 0:
        await ctx.send("No users in the watchlist")
    else:
        # Send back watchlist
        message = "## Watchlist\n"
        for i, user in enumerate(watchlist[ctx.guild.id]):
            message += f"{i+1}. <@{user.id}>\n"
        await ctx.send(message)

@bot.command()
async def remove(ctx, name: str):
    if ctx.channel.id != MOD_LOG_CHANNEL_ID and ctx.channel.id != MOD_CHAT_CHANNEL_ID:
        return 
    if ctx.guild.id not in watchlist:
        watchlist[ctx.guild.id] = []
    if ctx.guild.id not in whitelist:
        whitelist[ctx.guild.id] = []
    act_user = None
    async for member in ctx.guild.fetch_members(limit=None):
        if member.display_name == name:
            act_user = member
            break
    if not act_user:
        await ctx.send(f"User with name {name} is not a part of this server")
        return
    rem_user = None
    for user in watchlist[ctx.guild.id]:
        if user.display_name == name:
            rem_user = user
            break
    if rem_user:
        watchlist[ctx.guild.id].remove(rem_user)
        if rem_user not in whitelist[ctx.guild.id]:
            whitelist[ctx.guild.id].append(rem_user)
        await ctx.send(f"Removed <@{rem_user.id}> from the watchlist, and adding them to the whitelist")
    else:
        await ctx.send(f"{name} was not in the watchlist, not removing")

@bot.command()
async def add(ctx, name: str):
    if ctx.channel.id != MOD_LOG_CHANNEL_ID and ctx.channel.id != MOD_CHAT_CHANNEL_ID:
        return 
    if ctx.guild.id not in watchlist:
        watchlist[ctx.guild.id] = []
    if ctx.guild.id not in whitelist:
        whitelist[ctx.guild.id] = []
    cur_watchlist = watchlist[ctx.guild.id]
    cur_whitelist = whitelist[ctx.guild.id]
    async for member in ctx.guild.fetch_members(limit=None):
        if member.display_name == name:
            if member not in watchlist[ctx.guild.id]:
                watchlist[ctx.guild.id].append(member)
            if member in whitelist[ctx.guild.id]:
                whitelist[ctx.guild.id].remove(member)
            await ctx.send(f"Added <@{member.id}> to the watchlist")
            return
    await ctx.send(f"{name} is not a member of this server")

@bot.command()
async def get(ctx):
    if ctx.channel.id != MOD_LOG_CHANNEL_ID and ctx.channel.id != MOD_CHAT_CHANNEL_ID:
        return
    if ctx.guild.id not in watchlist:
        watchlist[ctx.guild.id] = []
    if ctx.guild.id not in whitelist:
        whitelist[ctx.guild.id] = []
    watchlist_str = ""
    whitelist_str = ""
    if len(watchlist[ctx.guild.id]) == 0:
        watchlist_str = "No users in the watchlist"
    else:
        # Send back watchlist
        watchlist_str = "## Watchlist\n"
        for i, user in enumerate(watchlist[ctx.guild.id]):
            watchlist_str += f"{i+1}. <@{user.id}>\n"
    if len(whitelist[ctx.guild.id]) == 0:
        whitelist_str = "No users in the whitelist"
    else:
        # Send back whitelist
        whitelist_str = "## Whitelist\n"
        for i, user in enumerate(whitelist[ctx.guild.id]):
            whitelist_str += f"{i+1}. <@{user.id}>\n"
    await ctx.send(watchlist_str + "\n" + whitelist_str)

@bot.command(name="help")
async def help_command(ctx):
    if ctx.channel.id != MOD_LOG_CHANNEL_ID and ctx.channel.id != MOD_CHAT_CHANNEL_ID:
        return 
    await ctx.send(
        "**Available Commands**\n"
        "`?init` - Reset the whitelist and set the watchlist according to a certain date range, usage: `?init years months days hours`\n"
        "`?add` - Add a member to the watchlist\n"
        "`?remove` - Remove a member from the watchlist\n"
        "`?get` - Get the current watchlist and whitelist without overwriting previous adds/removes\n"
    )

@bot.listen("on_message")
async def monitor_watchlist(message):
    if message.author.bot:
        return

    if message.author in watchlist.get(message.guild.id, []):
        if message.guild.id not in mod_log_channel_dict:
            return
        channel = bot.get_channel(mod_log_channel_dict[message.guild.id])
        await channel.send(f"<@{message.author.id}> sent {message.content}") 

@bot.listen("on_ready")
async def bot_ready():
    print(f"Logged in as {bot.user}")
    print("Registered commands:", [cmd.name for cmd in bot.commands])

@bot.listen("on_member_join")
async def monitor_new_member(member):
    duration = relativedelta(years=1, months=0, days=0, hours=0)
    cutoff = datetime.now(timezone.utc) - duration
    if member.created_at > cutoff:
        if member.guild.id not in watchlist:
            watchlist[member.guild.id] = [member]
        else:
            watchlist[member.guild.id].append(member)
            await mod_log_channel_dict[member.guild.id].send(f"Adding <@{member.id}> to the watchlist")

@bot.listen("on_member_remove")
async def monitor_leaving_member(member):
    if member.guild.id not in watchlist:
        watchlist[member.guild.id] = []
        return
    elif member not in watchlist[member.guild.id]:
        return
    else:
        watchlist[member.guild.id].remove(member)
        await mod_log_channel_dict[member.guild.id].send(f"Removing <@{member.id}> from the watchlist")

bot.run(TOKEN)
