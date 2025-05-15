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
bot_pause = False

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
    if not show_queue():
        autoDisconnect.start()
        return
    coro = play(ctx, url=None)
    future = asyncio.run_coroutine_threadsafe(coro, ctx.bot.loop)
    try:
        future.result()
    except Exception as e:
        print(f"Error in after_song: {e}")

def show_queue():
    with open("queue", 'r') as queue:
        lines = queue.readlines()
    return lines

@bot.event
async def on_ready():
    open("queue", 'w').close()
    print(f'Bot connected as {bot.user}')


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
            queue = show_queue()
            str = ""
            index = 1
            for i in range(1,len(queue),2):
                str += f"{index}. {queue[i]}"
                index += 1
            await ctx.send(f"Adding the song to the queue:\n{str}")
            return
    
    audio_url, audio_name = pop_queue()
    if not audio_url:
        await ctx.send("No more songs in the queue.")
        return
    source = discord.FFmpegPCMAudio(audio_url,before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
    ctx.voice_client.play(source, after=partial(after_song, ctx))
    bot_pause = False
    await ctx.send(f"Now playing: {audio_name}")

@bot.command()
async def pause(ctx):
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.pause()
        bot_pause = True
        await ctx.send("⏸️ Paused the music.")
    else:
        await ctx.send("There's nothing playing right now.")

@bot.command()
async def resume(ctx):
    vc = ctx.voice_client
    if vc and vc.is_paused():
        vc.resume()
        bot_pause = False
        await ctx.send("▶️ Resumed the music.")
    else:
        await ctx.send("The music isn't paused.")

@bot.command()
async def stop(ctx):
    vc = ctx.voice_client
    if vc:
        vc.stop()
        await ctx.send("⏹️ Stopped the music.")
        await vc.disconnect()
    else:
        await ctx.send("I'm not connected to a voice channel.")

@bot.command()
async def sq(ctx):
    if not show_queue():
        await ctx.send("🚫 The queue is empty. Add some songs to keep the party going!")
        return
    song_in_queue = []
    str = ""
    lines = show_queue()
    if lines:
        for i in range(1, len(lines), 2):
            song_in_queue.append(lines[i])
    for i in range(len(song_in_queue)):
        str += f"{i+1}. {song_in_queue[i]}"
    await ctx.send(f"📃 The queue:\n{str}")

@bot.command()
async def skip(ctx):
    if not show_queue():
        await ctx.send("🚫 The queue is empty.")
        return
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.stop()

@bot.command()
async def jump(ctx, index: int):
    vc = ctx.voice_client
    if vc:
        lines = show_queue()
        if index > len(lines)/2:
            await ctx.send("🚫 Invalid index.")
            return
        for i in range(index-1):
            pop_queue()
        vc.stop()
        await ctx.send(f"Jump to song {index} position in queue!")
    else:
        await ctx.send("I'm not connected to a voice channel.")

@bot.command()
async def remove(ctx, index: int):
    vc = ctx.voice_client
    if vc:
        lines = show_queue()
        if index > len(lines)/2:
            await ctx.send("🚫 Invalid index.")
            return
        with open("queue", 'w') as queue:
            queue.writelines(lines[:index*2-2])
            queue.writelines(lines[index*2:])
        await ctx.send(f"Remove song {index} position in queue!")
        await sq(ctx)
    else:
        await ctx.send("I'm not connected to a voice channel.")

@bot.command()
async def clear(ctx):
    vc = ctx.voice_client
    if vc:
        lines = show_queue()
        if not lines:
            await ctx.send("🚫 The queue is empty.")
            return
        open("queue", 'w').close()
        await ctx.send("🗑️ Queue cleared!")
    else:
        await ctx.send("I'm not connected to a voice channel.")

@bot.command()
async def top(ctx, index: int):
    vc = ctx.voice_client
    if vc:
        lines = show_queue()
        if not lines:
            await ctx.send("🚫 The queue is empty.")
            return
        with open("queue", 'w') as queue:
            queue.writelines(lines[index*2-2:index*2])
            queue.writelines(lines[:index*2-2])
            queue.writelines(lines[index*2:])
    else:
        await ctx.send("I'm not connected to a voice channel.")


@tasks.loop(seconds=200)
async def autoDisconnect():
    for guild in bot.guilds:
        vc = guild.voice_client
        if vc and not vc.is_playing() and not bot_pause:
            await vc.disconnect()

bot.run(token)
