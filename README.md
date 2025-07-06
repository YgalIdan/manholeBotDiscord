# 🎶 Manhole Music Bot

A lightweight and updated Discord music bot written in Python using `discord.py v2` and full support for **slash commands** (`/command` interface).  
Plays music from YouTube by URL or search query, manages queue and playlists, and auto-disconnects when idle.

> ✅ **Current version: v2.1.0**  
> ✨ Added full playlist support and improved stop command behavior.

---

## 🚀 What's New in v2.1.0

- ✅ **Full playlist support**  
  Now you can load and play entire playlists seamlessly, with continuous playback of multiple tracks.  

- ✅ **Stop command fix**  
  When using `/stop`, the entire queue is now cleared automatically to prevent leftover songs in the queue.

- ✅ Minor bug fixes and performance improvements.

---

## 🛠️ Available Slash Commands

All commands must be used with `/` in any text channel where the bot is active.

### 🎵 `/play <query or playlist URL>`
Play a song or an entire playlist from a YouTube URL or search term.
- If `<query>` is a YouTube video URL or search term, plays the song or queues it.
- If a playlist URL is provided, queues all songs in the playlist for continuous playback.

### ⏸️ `/pause`
Pause the currently playing song.

### ▶️ `/resume`
Resume playback if paused.

### ⏹️ `/stop`
Stop playback and disconnect the bot from the voice channel.  
**Note:** This now also clears the entire queue.

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
  New songs or playlists added while one is playing will queue up automatically.
  
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
   git clone https://github.com/YgalIdan/manholeBotDiscord.git
   cd manholeBotDiscord
