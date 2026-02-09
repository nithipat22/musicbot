import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os

# ========================
# Intents (แก้ Error)
# ========================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ========================
# YTDLP Config
# ========================
ytdlp_opts = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
}

ffmpeg_opts = {
    "options": "-vn"
}

ytdlp = yt_dlp.YoutubeDL(ytdlp_opts)

# ========================
# Events
# ========================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# ========================
# Music System
# ========================
queue = []

async def play_next(ctx):
    if len(queue) == 0:
        await ctx.send("📭 ไม่มีเพลงในคิวแล้ว")
        return

    url = queue.pop(0)

    with ytdlp:
        info = ytdlp.extract_info(url, download=False)
        url2 = info["url"]
        title = info["title"]

    source = await discord.FFmpegOpusAudio.from_probe(
        url2,
        **ffmpeg_opts
    )

    vc = ctx.voice_client

    vc.play(
        source,
        after=lambda e: asyncio.run_coroutine_threadsafe(
            play_next(ctx),
            bot.loop
        )
    )

    await ctx.send(f"▶️ กำลังเล่น: **{title}**")


# ========================
# Commands
# ========================

@bot.command()
async def join(ctx):
    if ctx.author.voice is None:
        await ctx.send("❌ เข้าห้องเสียงก่อนนะ")
        return

    await ctx.author.voice.channel.connect()
    await ctx.send("✅ เข้าห้องแล้ว")


@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 ออกห้องแล้ว")


@bot.command()
async def play(ctx, url: str):
    if ctx.voice_client is None:
        await join(ctx)

    queue.append(url)

    if not ctx.voice_client.is_playing():
        await play_next(ctx)
    else:
        await ctx.send("➕ เพิ่มเข้า Queue แล้ว")


@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ ข้ามเพลงแล้ว")


@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        queue.clear()
        ctx.voice_client.stop()
        await ctx.send("⏹️ หยุดหมดแล้ว")


@bot.command()
async def queue_list(ctx):
    if len(queue) == 0:
        await ctx.send("📭 คิวว่าง")
        return

    msg = "🎶 คิวเพลง:\n"

    for i, song in enumerate(queue, start=1):
        msg += f"{i}. {song}\n"

    await ctx.send(msg)


# ========================
# Run Bot
# ========================
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("❌ ไม่เจอ TOKEN ใน Environment")
else:
    bot.run(TOKEN)
