# 🎶 Manhole Music Bot

A lightweight and easy-to-use Discord music bot written in Python using `discord.py`.  
Supports queueing, playback control, and automatic behavior handling.

---

## 📦 Features

- Play music from YouTube links
- Automatic queue handling
- Auto-disconnect when idle
- Simple and clear commands

---

## 🛠️ Commands

### ▶️ `!play <url>`
Plays a song from the provided URL (YouTube).  
- If a song is already playing, the new song is added to the end of the queue.
- The current queue is displayed after adding the song.

### ⏸️ `!pause`
Pauses the currently playing song.

### ⏯️ `!resume`
Resumes playback of a paused song.

### ⏹️ `!stop`
Stops playback and clears the queue.

### 📃 `!sq`
Displays the current queue of songs in order.

---

## ⚙️ Automatic Behaviors

- ✅ **Queue System**:  
  Songs added while one is already playing are placed at the end of the queue.

- ✅ **Auto-Playback**:  
  When a song ends, the next song in the queue is automatically played.

- ✅ **Auto-Disconnect**:  
  If no songs are playing and the queue is empty, the bot disconnects from the voice channel automatically after a short delay.

---

## 🚀 Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/YgalIdan/manhole-music-bot.git
