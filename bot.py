import os
import discord
from discord.ext import commands, tasks
import yt_dlp
import asyncio
from functools import partial

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

def add_to_queue(youtube_url):
    with open("queue", 'a') as queue:
        ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'default_search': 'auto',
        'noplaylist': True,
        'extract_flat': 'in_playlist',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            queue.write(info['url'] + '\n' + info['title'] + '\n')

def pop_queue():
    with open("queue", 'r') as queue:
        lines = queue.readlines()
        if lines:
            audio_url = lines[0].strip()
            audio_name = lines[1].strip()
            with open("queue", 'w') as queue:
                queue.writelines(lines[2:])
            return audio_url, audio_name
        else:
            return None

def after_song(ctx, error=None):
    coro = play(ctx, url=None)
    future = asyncio.run_coroutine_threadsafe(coro, ctx.bot.loop)
    try:
        future.result()
    except Exception as e:
        print(f"Error in after_song: {e}")

def show_queue():
    with open("queue", 'r') as queue:
        lines = queue.readlines()
    song_in_queue = []
    str = ""
    if lines:
        for i in range(1, len(lines), 2):
            song_in_queue.append(lines[i])
    for i in range(len(song_in_queue)):
        str += f"{i+1}. {song_in_queue[i]}"
    return str

@bot.event
async def on_ready():
    open("queue", 'w').close()
    print(f'Bot connected as {bot.user}')
    autoDisconnect.start()


@bot.command()
async def play(ctx, url):
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("You're not in a voice channel!")

    if url:
        add_to_queue(url)
        if ctx.voice_client and ctx.voice_client.is_playing():
            await ctx.send(f"Adding the song to the queue:\n{show_queue()}")
            return
    
    audio_url, audio_name = pop_queue()
    if not audio_url:
        await ctx.send("No more songs in the queue.")
        return
    source = discord.FFmpegPCMAudio(audio_url,before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
    ctx.voice_client.play(source, after=partial(after_song, ctx))
    await ctx.send(f"Now playing: {audio_name}")

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

@bot.command()
async def sq(ctx):
    if not show_queue():
        await ctx.send(" The queue is empty. Add some songs to keep the party going!")
        return
    await ctx.send(f" The queue:\n{show_queue()}")

@tasks.loop(seconds=60)
async def autoDisconnect():
    for guild in bot.guilds:
        vc = guild.voice_client
        if vc and not vc.is_playing():
            await vc.disconnect()

bot.run(token)