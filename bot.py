import os
import discord
from discord.ext import commands, tasks
from discord import app_commands
import yt_dlp
import asyncio
from yt_dlp import YoutubeDL

token = os.getenv("TOKEN_BOT")
start_with = os.getenv("START_WITH")
GUILD_Id = discord.Object(id=797091616807583745)


if token:
    print("Token loaded successfully.")
else:
    print("Token not found.")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
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


def show_queue():
    with open("queue", 'r') as queue:
        lines = queue.readlines()
    return lines


def build_queue():
    song_in_queue = []
    str = "📃 The queue:\n"
    lines = show_queue()
    if lines:
        for i in range(1, len(lines), 2):
            song_in_queue.append(lines[i])
    for i in range(len(song_in_queue)):
        str += f"{i+1}. {song_in_queue[i]}"

    return str


def search_youtube(query):
    with YoutubeDL({'quiet': True}) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            return info['webpage_url']
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return None


async def play_next_song(vc, interaction=None):
    result = pop_queue()
    if result:
        audio_url, audio_name = result
        source = discord.FFmpegPCMAudio(audio_url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
        vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next_song(vc, interaction), bot.loop))
        if interaction:
            await interaction.followup.send(f"▶️ Now playing: {audio_name}")
    else:
        if interaction:
            await interaction.followup.send("🚫 Queue is empty.")


@bot.tree.command(name="play", description="Play a song from YouTube", guild=GUILD_Id)
@app_commands.describe(query="YouTube URL or Name of song")
async def play(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    
    if not interaction.user.voice:
        await interaction.followup.send("❌ You are not in a voice channel.")
        return

    vc = interaction.guild.voice_client
    if not vc:
        vc = await interaction.user.voice.channel.connect()

    if "http" in query:
        add_to_queue(query)
    else:
        add_to_queue(search_youtube(query))

    if vc.is_playing():
        queue = show_queue()
        queue_str = ""
        index = 1
        for i in range(1, len(queue), 2):
            queue_str += f"{index}. {queue[i]}"
            index += 1
        await interaction.followup.send(f"🎶 Added to queue:\n{queue_str}")
    else:
        await play_next_song(vc, interaction)


@bot.tree.command(name="pause", description="Pause a song", guild=GUILD_Id)
async def pause(interaction: discord.Interaction):
    await interaction.response.defer()

    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.pause()
        global bot_pause
        bot_pause = True
        await interaction.followup.send("⏸️ Paused the music.")
    else:
        await interaction.followup.send("There's nothing playing right now.")


@bot.tree.command(name="resume", description="Resume a song", guild=GUILD_Id)
async def resume(interaction: discord.Interaction):
    await interaction.response.defer()

    vc = interaction.guild.voice_client
    if vc and vc.is_paused():
        vc.resume()
        global bot_pause
        bot_pause = False
        await interaction.followup.send("▶️ Resumed the music.")
    else:
        await interaction.followup.send("The music isn't paused.")


@bot.tree.command(name="stop", description="Stop a song", guild=GUILD_Id)
async def stop(interaction: discord.Interaction):
    await interaction.response.defer()
    vc = interaction.guild.voice_client
    if vc:
        vc.stop()
        await interaction.followup.send("⏹️ Stopped the music.")
        await vc.disconnect()
    else:
        await interaction.followup.send("I'm not connected to a voice channel.")


@bot.tree.command(name="sq", description="Show a queue", guild=GUILD_Id)
async def sq(interaction: discord.Interaction):
    await interaction.response.defer()

    if not show_queue():
        await interaction.followup.send("🚫 The queue is empty. Add some songs to keep the party going!")
        return
    queue_msg = build_queue()
    await interaction.followup.send(queue_msg)


@bot.tree.command(name="skip", description="Skip a song", guild=GUILD_Id)
async def skip(interaction: discord.Interaction):
    await interaction.response.defer()

    if not show_queue():
        await interaction.followup.send("🚫 The queue is empty.")
        return
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await interaction.followup.send("⏭️ Skipped to the next song!")


@bot.tree.command(name="jump", description="Jump a song in queue", guild=GUILD_Id)
@app_commands.describe(index="Jump to number song in queue")
async def jump(interaction: discord.Interaction, index: int):
    await interaction.response.defer()

    vc = interaction.guild.voice_client
    if vc:
        lines = show_queue()
        if index > len(lines)/2:
            await interaction.followup.send("🚫 Invalid index.")
            return
        for i in range(index-1):
            pop_queue()
        vc.stop()
        await interaction.followup.send(f"Jump to song {index} position in queue!")
    else:
        await interaction.followup.send("I'm not connected to a voice channel.")


@bot.tree.command(name="remove", description="Remove a song from queue", guild=GUILD_Id)
@app_commands.describe(index="Remove a number song in queue")
async def remove(interaction: discord.Interaction, index: int):
    await interaction.response.defer()

    vc = interaction.guild.voice_client
    if vc:
        lines = show_queue()
        if index > len(lines)/2:
            await interaction.followup.send("🚫 Invalid index.")
            return
        with open("queue", 'w') as queue:
            queue.writelines(lines[:index*2-2])
            queue.writelines(lines[index*2:])
        await interaction.followup.send(f"Remove song {index} position in queue!")
        queue_msg = build_queue()
        await interaction.followup.send(queue_msg)
    else:
        await interaction.followup.send("I'm not connected to a voice channel.")


@bot.tree.command(name="clear", description="Clear a queue", guild=GUILD_Id)
async def remove(interaction: discord.Interaction):
    await interaction.response.defer()

    vc = interaction.guild.voice_client
    if vc:
        lines = show_queue()
        if not lines:
            await interaction.followup.send("🚫 The queue is empty.")
            return
        open("queue", 'w').close()
        await interaction.followup.send("🗑️ Queue cleared!")
    else:
        await interaction.followup.send("I'm not connected to a voice channel.")


@bot.tree.command(name="top", description="Move a song to top a queue", guild=GUILD_Id)
@app_commands.describe(index="Move a song number to top queue")
async def top(interaction: discord.Interaction, index: int):
    await interaction.response.defer()

    vc = interaction.guild.voice_client
    if vc:
        lines = show_queue()
        if not lines:
            await interaction.followup.send("🚫 The queue is empty.")
            return
        with open("queue", 'w') as queue:
            queue.writelines(lines[index*2-2:index*2])
            queue.writelines(lines[:index*2-2])
            queue.writelines(lines[index*2:])
            await interaction.followup.send(f"⬆️ Moved song #{index} to the top of the queue!")
    else:
        await interaction.followup.send("I'm not connected to a voice channel.")


@tasks.loop(seconds=200)
async def autoDisconnect():
    for guild in bot.guilds:
        vc = guild.voice_client
        if vc and not vc.is_playing() and not bot_pause:
            await vc.disconnect()


@bot.event
async def on_ready():
    open("queue", 'w').close()
    guild = discord.Object(id=797091616807583745)
    synced = await bot.tree.sync(guild=guild)
    print(f"✅ Synced {len(synced)} commands to {guild.id}")
    print(f'Bot connected as {bot.user}')
    autoDisconnect.start()


bot.run(token)
