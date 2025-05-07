import os
import discord
from discord.ext import commands, tasks
import yt_dlp

token = os.getenv("TOKEN_BOT")
start_with = os.getenv("START_WITH")

if token:
    print("Token loaded successfully.")
else:
    print("Token not found.")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix=start_with, intents=intents)

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')
    autoDisconnect.start()

@bot.command()
async def test(ctx):
    await ctx.send("hello, i ready")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Left the voice channel.")
    else:
        await ctx.send("I'm not in a voice channel!")

@bot.command()
async def play(ctx, url):
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("You're not in a voice channel!")

    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'default_search': 'auto',
        'noplaylist': True,
        'extract_flat': 'in_playlist',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']

    before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
    source = discord.FFmpegPCMAudio(audio_url,before_options=before_options)
    ctx.voice_client.stop()
    ctx.voice_client.play(source)
    await ctx.send(f"Now playing: {info['title']}")

@bot.command()
async def pause(ctx):
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await ctx.send("⏸️ Paused the music.")
    else:
        await ctx.send("There's nothing playing right now.")

@bot.command()
async def resume(ctx):
    vc = ctx.voice_client
    if vc and vc.is_paused():
        vc.resume()
        await ctx.send("▶️ Resumed the music.")
    else:
        await ctx.send("The music isn't paused.")

@bot.command()
async def stop(ctx):
    vc = ctx.voice_client
    if vc:
        vc.stop()
        await ctx.send("⏹️ Stopped the music.")
    else:
        await ctx.send("I'm not connected to a voice channel.")

@tasks.loop(seconds=60)
async def autoDisconnect():
    for guild in bot.guilds:
        vc = guild.voice_client
        if vc and not vc.is_playing():
            await vc.disconnect()

bot.run(token)