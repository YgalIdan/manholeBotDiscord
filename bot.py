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

    result = {
        "url": url,
        "title": info.get("title", "Unknown Title"),
        "thumbnail": info.get("thumbnail"),
        "duration": info.get("duration", 0),
        "webpage_url": info.get("webpage_url"),
    }

    youtube_cache[key] = (
        time.time(),
        result,
    )

    return result


# --- PLAY LOOP (ONE TASK ONLY!) ---
async def player_loop(vc, interaction):
    global now_playing

    while True:
        song = await song_queue.get()
        url = song["url"]
        title = song["title"]

        now_playing = song

        source = discord.FFmpegPCMAudio(
            url,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        )

        try:
            vc.play(source)
        except Exception as e:
            print(f"Play error: {e}")
            continue

        if interaction:
            embed = discord.Embed(
                title="🎵 Now Playing",
                description=f"### [{title}]({song['webpage_url']})",
                color=discord.Color.red(),
            )

            if song.get("thumbnail"):
                embed.set_thumbnail(url=song["thumbnail"])

            embed.add_field(
                name="👤 Requested by",
                value=song["requester"].mention,
                inline=True,
            )

            duration = song.get("duration", 0)
            minutes, seconds = divmod(duration, 60)

            embed.add_field(
                name="⏱️ Duration",
                value=f"{minutes}:{seconds:02}",
                inline=True,
            )

            embed.add_field(
                name="📃 Queue",
                value=f"**{song_queue.qsize()}** songs waiting",
                inline=True
            )

            embed.set_footer(text="🎶 Manhole Music Bot")

            await interaction.channel.send(embed=embed)

        # Wait until finished
        while vc.is_playing() or vc.is_paused():
            await asyncio.sleep(1)

        now_playing = None

        if song_queue.empty():
            break  # queue empty → stop loop

    # Nothing left → disconnect
    if vc.is_connected():
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
        song = await asyncio.to_thread(search_youtube, query)
        song["requester"] = interaction.user
        await song_queue.put(song)
    except Exception as e:
        print(e)
        return await interaction.followup.send(
            "❌ Couldn't find a playable version of this song."
        )

    # If already playing → only add to queue
    if vc.is_playing() or vc.is_paused():
        return await interaction.followup.send(f"➕ Added to queue: **{song['title']}**")

    # Not playing → start play loop    
    bot.loop.create_task(player_loop(vc, interaction))
    await interaction.delete_original_response()


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

    embed = discord.Embed(
        title="📜 Music Queue",
        color=discord.Color.blurple()
    )

    for i, song in enumerate(tmp, start=1):
        embed.add_field(
            name=f"{i}. {song['title']}",
            value=f"👤 Requested by: **{song['requester'].mention}**",
            inline=False
        )

    await interaction.followup.send(embed=embed)


@bot.event
async def on_ready():
    guild = discord.Object(id=797091616807583745)
    if os.getenv("BOT_MODE") == "prod":
        synced = await bot.tree.sync(guild=guild)
        print(f"✅ Synced {len(synced)} commands.")
    else:
        bot.tree.clear_commands(guild=guild)
        await bot.tree.sync(guild=guild)
        print("Test mode - Slash commands not synced")
    
    print(f"Bot connected as {bot.user}")


bot.run(token)
