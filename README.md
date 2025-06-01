# 🎶 Manhole Music Bot

A lightweight and updated Discord music bot written in Python using `discord.py v2` and full support for **slash commands** (`/command` interface).  
Plays music from YouTube, manages queue, and auto-disconnects when idle.

> ✅ **Current version: v2.0.0**  
> ✨ Now using `discord.app_commands` instead of legacy `@bot.command`.

---

## 🚀 What's New in v2.0.0

- ✅ Full migration to [Slash Commands](https://discord.com/blog/slash-commands-are-here)
- ✅ All commands re-written using `discord.app_commands`
- ✅ Commands now support auto-complete, inline descriptions, and dynamic feedback
- ✅ Defer mechanism implemented to prevent webhook timeout issues
- ✅ Improved queue management (add, remove, jump, top)
- ✅ Better structure for `play_next_song()` logic

---

## 🛠️ Available Slash Commands

All commands must be used with `/` in any text channel where the bot is active.

### 🎵 `/play <query>`
Play a song from a YouTube URL or a search term.
- If `<query>` is a YouTube URL, it plays the specified song.
- If `<query>` is a search term (e.g., song name or artist), it searches YouTube and plays the top result.
- If a song is already playing, the new song or search result is added to the queue.
- If no song is playing, it plays immediately.

### ⏸️ `/pause`
Pause the currently playing song.

### ▶️ `/resume`
Resume playback if paused.

### ⏹️ `/stop`
Stop playback and disconnect the bot from the voice channel.

### 📃 `/sq`
Display the current queue in order.

### ⏭️ `/skip`
Skip the current song and automatically play the next one in queue.

### 🔢 `/jump <index>`
Jump to a specific song number in the queue.

### ❌ `/remove <index>`
Remove a specific song from the queue by its position.

### 🗑️ `/clear`
Clear the entire song queue.

### ⬆️ `/top <index>`
Move a specific song in the queue to the top.

---

## ⚙️ Automatic Behaviors

- ✅ **Auto-queue handling**  
  New songs added while one is playing will queue up automatically.
  
- ✅ **Auto-play next**  
  When a song ends, the next one plays immediately using a coroutine-safe callback.

- ✅ **Auto-disconnect**  
  If no audio is playing for 200 seconds, the bot disconnects automatically from the voice channel.

---

## 📦 Requirements

- Python 3.9+
- `discord.py` 2.0+
- `yt_dlp`
- `ffmpeg` installed and available in PATH

---

## 🧪 Local Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/manholeBotDiscord.git
   cd manholeBotDiscord
