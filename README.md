# 🎶 Manhole Music Bot

A lightweight Discord music bot written in Python using **discord.py v2** with modern **Slash Commands** support.

Play music directly from YouTube using a URL or search query, manage a queue, and enjoy a clean and responsive music experience.

> ✅ **Current version: v2.2.0**
> 🚀 Faster YouTube search, improved queue engine, redesigned "Now Playing" embeds and major internal improvements.

---

# 🚀 What's New in v2.2.0

### ⚡ Faster song search
- Improved YouTube searching.
- Cached search results for frequently requested songs.
- Search now runs in a background thread to keep the bot responsive.

### 🎵 Redesigned music player
- Beautiful **Now Playing** embed.
- Song thumbnail.
- Clickable YouTube title.
- Requester's name.
- Song duration.
- Remaining queue size.
- Automatic timestamp.

### 🔄 Improved playback engine
- Rewritten queue handling.
- Prevents multiple playback loops.
- Better playback stability.
- Improved voice connection handling.

### 🧪 Test / Production support
- Test bot can run without publishing Slash Commands.
- Production bot keeps the full Slash Command interface.

### 🛠 Improvements
- Better code structure.
- Improved error handling.
- General performance optimizations.

---

# 🛠 Available Slash Commands

## 🎵 `/play <song name | YouTube URL>`
Search for a song or play directly from YouTube.

## ⏸️ `/pause`
Pause playback.

## ▶️ `/resume`
Resume playback.

## ⏭️ `/skip`
Skip the current song.

## ⏹️ `/stop`
Stop playback, clear the queue and disconnect.

## 📜 `/sq`
Display the current queue.

---

# ⚙️ Features

- 🎵 YouTube search
- 🚀 Fast cached lookups
- 📃 Queue management
- 🖼 Rich "Now Playing" embeds
- ⏭ Automatic next song
- 🔄 Stable playback loop
- 🎧 Automatic voice disconnect when queue ends
- 🧪 Separate Test and Production modes

---

# 📦 Requirements

- Python 3.13+
- discord.py 2.5+
- yt-dlp
- FFmpeg

---

# 🧪 Local Development

```bash
git clone https://github.com/YgalIdan/manholeBotDiscord.git
cd manholeBotDiscord
pip install -r requirements.txt
python bot.py