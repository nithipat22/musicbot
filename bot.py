import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os

# ==========================
# INTENTS (ไม่ต้อง privileged)
# ==========================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ==========================
# YTDLP CONFIG
# ==========================
ytdlp_opts = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
}

ffmpeg_opts = {
    "options": "-vn"
}

ytdlp = yt_dlp.YoutubeDL(ytdlp_opts)

# ==========================
# EVENT
# ==========================
@bot.event
async def on_ready():
    print("================================")
    print(f"✅ Logged in as {bot.user}")
    print("🎵 Music Bot Ready!")
    print("================================")


# ==========================
# MUSIC QUEUE
# ==========================
queue = []


async def play_next(ctx):
    if not queue:
        await ctx.send("📭 คิวหมดแล้ว")
        return

    url = queue.pop(0)

    with ytdlp:
        info = ytdlp.extract_info(url, download=False)
        stream_url = info["url"]
        title = info["title"]

    source = await discord.FFmpegOpusAudio.from_probe(
        stream_url,
        **ffmpeg_opts
    )

    vc = ctx.voice_client

    def after_play(err):
        if err:
            print("Error:", err)

        fut = asyncio.run_coroutine_threadsafe(
            play_next(ctx),
            bot.loop
        )

        try:
            fut.result()
        except:
            pass

    vc.play(source, after=after_play)

    await ctx.send(f"▶️ เล่น: **{title}**")


# ==========================
# COMMANDS
# ==========================

@bot.command()
async def join(ctx):

    if not ctx.author.voice:
        await ctx.send("❌ เข้าห้องเสียงก่อน")
        return

    channel = ctx.author.voice.channel

    if ctx.voice_client:
        await ctx.voice_client.move_to(channel)
    else:
        await channel.connect()

    await ctx.send("✅ เข้าห้องแล้ว")


@bot.command()
async def leave(ctx):

    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 ออกแล้ว")


@bot.command()
async def play(ctx, url: str):

    if not ctx.voice_client:
        await join(ctx)

    queue.append(url)

    if not ctx.voice_client.is_playing():
        await play_next(ctx)
    else:
        await ctx.send("➕ เพิ่มเข้าคิวแล้ว")


@bot.command()
async def skip(ctx):

    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ ข้ามแล้ว")


@bot.command()
async def stop(ctx):

    if ctx.voice_client:
        queue.clear()
        ctx.voice_client.stop()
        await ctx.send("⏹️ หยุดหมดแล้ว")


@bot.command(name="queue")
async def show_queue(ctx):

    if not queue:
        await ctx.send("📭 คิวว่าง")
        return

    msg = "🎶 คิวเพลง:\n"

    for i, song in enumerate(queue, 1):
        msg += f"{i}. {song}\n"

    await ctx.send(msg)


# ==========================
# RUN
# ==========================
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("❌ ไม่เจอ TOKEN ใน Environment")
else:
    bot.run(TOKEN)
