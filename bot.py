import os
import time
import discord
from discord.ext import commands, tasks
from discord import app_commands
import yt_dlp
import asyncio

token = os.getenv("TOKEN_BOT")
start_with = os.getenv("START_WITH")
GUILD_Id = discord.Object(id=797091616807583745)

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix=start_with, intents=intents)

YDL_OPTS = {
    "quiet": True,
    "noplaylist": True,
    "default_search": "ytsearch",
    "format": "bestaudio/best",
    "skip_download": True,
    "extract_flat": False,
}

ydl = yt_dlp.YoutubeDL(YDL_OPTS)

youtube_cache = {}
CACHE_TTL = 60 * 60

# --- NEW: REAL QUEUE IN MEMORY ---
song_queue = asyncio.Queue()
now_playing = None
bot_paused = False


# --- YOUTUBE SEARCH ---
def search_youtube(query: str):
    key = query.lower().strip()

    # Cache
    cached = youtube_cache.get(key)
    if cached:
        ts, value = cached

        if time.time() - ts < CACHE_TTL:
            return value

        del youtube_cache[key]

    info = ydl.extract_info(query, download=False)

    if "entries" in info:
        info = next((e for e in info["entries"] if e), None)

    if info is None:
        raise Exception("No search results")

    url = info.get("url")

    if not url:
        formats = info.get("formats", [])

        audio_formats = [
            f for f in formats
            if f.get("acodec") != "none"
            and f.get("url")
        ]

        if audio_formats:
            audio_formats.sort(
                key=lambda f: f.get("abr") or 0,
                reverse=True,
            )

            url = audio_formats[0]["url"]

    if not url:
        raise Exception("No playable audio stream")

    result = (
        url,
        info.get("title", "Unknown Title")
    )

    youtube_cache[key] = (
        time.time(),
        result,
    )

    return result


# --- PLAY LOOP (ONE TASK ONLY!) ---
async def player_loop(vc, interaction):
    global now_playing

    while True:
        url, title = await song_queue.get()
        now_playing = title

        source = discord.FFmpegPCMAudio(
            url,
            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
        )

        vc.play(source)

        if interaction:
            await interaction.followup.send(f"🎵 Now playing: **{title}**")

        # Wait until finished
        while vc.is_playing() or vc.is_paused():
            await asyncio.sleep(1)

        now_playing = None

        if song_queue.empty():
            break  # queue empty → stop loop

    # Nothing left → disconnect
    await vc.disconnect()


# ======================= COMMANDS =======================

@bot.tree.command(name="play", description="Play a song", guild=GUILD_Id)
@app_commands.describe(query="YouTube URL or song name")
async def play(interaction: discord.Interaction, query: str):
    await interaction.response.defer(thinking=True)

    # Must be in voice
    if not interaction.user.voice:
        return await interaction.followup.send("❌ You must be in a voice channel.")

    vc = interaction.guild.voice_client

    # Join channel if needed
    if not vc:
        vc = await interaction.user.voice.channel.connect()

    # Search YouTube
    try:
        url, title = await asyncio.to_thread(search_youtube, query)
    except Exception as e:
        print(e)
        return await interaction.followup.send(
            "❌ Couldn't find a playable version of this song."
        )

    # Add to queue
    await song_queue.put((url, title))

    # If already playing → only add to queue
    if vc.is_playing() or vc.is_paused():
        return await interaction.followup.send(f"➕ Added to queue: **{title}**")

    # Not playing → start play loop
    await interaction.followup.send(f"🎶 Starting queue with: **{title}**")
    bot.loop.create_task(player_loop(vc, interaction))


@bot.tree.command(name="skip", description="Skip song", guild=GUILD_Id)
async def skip(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.stop()
        return await interaction.followup.send("⏭️ Skipped!")
    await interaction.followup.send("Nothing is playing.")


@bot.tree.command(name="pause", description="Pause", guild=GUILD_Id)
async def pause(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.pause()
        return await interaction.followup.send("⏸️ Paused.")
    await interaction.followup.send("Nothing is playing.")


@bot.tree.command(name="resume", description="Resume", guild=GUILD_Id)
async def resume(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    vc = interaction.guild.voice_client
    if vc and vc.is_paused():
        vc.resume()
        return await interaction.followup.send("▶️ Resumed.")
    await interaction.followup.send("Nothing is paused.")


@bot.tree.command(name="stop", description="Stop music", guild=GUILD_Id)
async def stop(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    vc = interaction.guild.voice_client
    if vc:
        while not song_queue.empty():
            song_queue.get_nowait()
        vc.stop()
        await vc.disconnect()
        return await interaction.followup.send("⏹️ Stopped and disconnected.")
    await interaction.followup.send("Bot is not in voice.")


@bot.tree.command(name="sq", description="Show queue", guild=GUILD_Id)
async def sq(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    if song_queue.empty():
        return await interaction.followup.send("📭 Queue is empty.")

    tmp = list(song_queue._queue)

    msg = "📃 **Queue:**\n"
    for i, (_, title) in enumerate(tmp, start=1):
        msg += f"**{i}.** {title}\n"

    await interaction.followup.send(msg)


@bot.event
async def on_ready():
    guild = discord.Object(id=797091616807583745)
    synced = await bot.tree.sync(guild=guild)
    print(f"✅ Synced {len(synced)} commands.")
    print(f"Bot connected as {bot.user}")


bot.run(token)
