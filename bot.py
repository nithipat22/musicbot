import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os

# เปิด Intent
intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)

# ตั้งค่า yt-dlp
YDL_OPTIONS = {
    "format": "bestaudio",
    "noplaylist": True
}

# ตั้งค่า ffmpeg
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}


@bot.event
async def on_ready():
    print(f"✅ Online: {bot.user}")


# เข้าห้องเสียง
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
    else:
        await ctx.send("❌ เข้า VC ก่อนนะ")


# ออกห้องเสียง
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()


# เล่นเพลง
@bot.command()
async def play(ctx, *, search):

    if not ctx.author.voice:
        await ctx.send("❌ เข้า VC ก่อน")
        return

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(f"ytsearch:{search}", download=False)
        url = info["entries"][0]["url"]
        title = info["entries"][0]["title"]

    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    source = await discord.FFmpegOpusAudio.from_probe(
        url, **FFMPEG_OPTIONS
    )

    ctx.voice_client.play(source)

    await ctx.send(f"🎵 กำลังเล่น: **{title}**")


# หยุด
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()


# อ่าน Token จาก Railway
TOKEN = os.getenv("TOKEN")

bot.run(TOKEN)
