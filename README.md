# Friend Group Soundboard

A soundboard that builds its grid from whatever `.mp3` (or `.wav`/`.ogg`/`.m4a`)
files are sitting in the `sounds` folder — no list to maintain, no code to
edit. Drop a file in, refresh the page, it's a tile.

Right now it plays on whichever computer has it open (browser audio can't be
piped into another app on its own). See **Roadmap** below for the plan to
get a sound to play *into* a Discord voice channel for everyone.

## What's in here

```
discord-soundboard/
├── index.html      ← the app: grid + "add a sound" panel
├── serve.py        ← the tiny local server that makes auto-scanning possible
├── start.command   ← double-click to launch on Mac
├── start.bat       ← double-click to launch on Windows
├── start.sh        ← run to launch on Linux
├── sounds/         ← your audio files live here
│   ├── beep.mp3    ← sample tones so the grid works before you add real clips
│   ├── ding.mp3
│   └── buzz.mp3
└── README.md
```

## Why there's a server now

A webpage opened by double-clicking it (`file://…`) is blocked by every
browser from looking inside its own folder or accepting a real file upload —
that's a security restriction, not something this app can work around.
`serve.py` is a small script (Python's standard library only, nothing to
install) that runs *on your own computer* and gives the page a real backend:
it lists what's actually in `sounds/` on every page load, and saves anything
uploaded through the panel straight into that folder. That's what makes
"just drop a file in and it shows up" possible.

## Launching it

You'll need Python 3 installed (Mac and Linux almost always have it already;
on Windows, install it from [python.org](https://www.python.org/downloads/)
if `python` isn't recognized — check "Add python.exe to PATH" during setup).

- **Mac:** double-click `start.command`. First time only, macOS may warn
  it's from an unidentified developer — right-click it and choose **Open**
  instead, once.
- **Windows:** double-click `start.bat`.
- **Linux:** run `./start.sh` (or `python3 serve.py`) from a terminal in
  this folder.

Any of these opens your browser to `http://localhost:8000` with the grid
already populated. Leave the terminal/command window open while you use it;
closing it stops the server. Press **Ctrl+C** in that window to stop it
cleanly.

## Adding a new sound

Two ways, both instant — no code, no restart needed:

1. **Through the page:** open **Add a new sound**, pick a file, type a
   display name, hit **Preview** to check it, then **Add to soundboard**.
   It's saved into `sounds/` and shows up in the grid right away.
2. **By hand:** just drop an audio file into the `sounds` folder yourself
   and click **Refresh** on the page (or reload it). The tile's name comes
   from the filename — `air-horn.mp3` becomes "Air Horn", `WOW.mp3` stays
   "WOW".

## Sharing sounds with your friends via GitHub

The server keeps everything local to your machine — it doesn't touch
GitHub by itself. To get a sound into the shared repo so friends running
their own copy get it too, commit and push the `sounds` folder whenever
it's convenient:

```bash
git add sounds/
git commit -m "Add new sounds"
git push
```

### First time putting this on GitHub

1. Go to [github.com/new](https://github.com/new), name the repo (e.g.
   `discord-soundboard`), keep it **Public**, and create it without a
   README (this one's already written).
2. On the repo page, **Add file → Upload files**, and drag in everything
   in this folder (including the `sounds` subfolder — GitHub preserves the
   structure).
3. Commit to `main`.

Or with git directly:

```bash
git init
git add .
git commit -m "Initial soundboard"
git branch -M main
git remote add origin https://github.com/<your-username>/discord-soundboard.git
git push -u origin main
```

Each friend who wants their own local copy clones the repo and launches it
the same way (`start.command` / `start.bat` / `start.sh`) — Python is the
only thing they need installed.

## Roadmap: making it play in the actual Discord call

This is the bigger step, whenever you're ready for it. The short version:

A browser tab (or this local server) can only make sound come out of *your*
speakers — nothing here can inject audio into someone else's app, including
Discord. To have a click be heard by the whole voice channel, something
needs to actually **join the call as a participant** and stream the audio
in. That's a Discord bot, and it needs:

- A bot application registered in the
  [Discord Developer Portal](https://discord.com/developers/applications),
  invited to your server with permission to connect/speak in voice channels.
- A small always-running Node.js process (`discord.js` +
  `@discordjs/voice`, plus `ffmpeg` for decoding) that joins your voice
  channel and plays a file from this same `sounds/` folder on command
  (a Discord slash command like `/play ding`, or this webpage calling an
  API the bot exposes).
- Somewhere for that process to run continuously — your own PC while
  everyone's in the call, a Raspberry Pi, or a cheap/free host (Railway,
  Fly.io, a small VPS).

Handy detail: `serve.py` is already "a small persistent process that
manages the sound files." The Discord bot phase is realistically an
extension of this same server (add a Discord client alongside the HTTP
one) rather than a throwaway rewrite — so nothing here is wasted work.
Come back when you're ready to build that part.

## Notes

- Sounds can overlap — clicking a second tile doesn't cut off the first.
- Keyboard shortcuts (shown on each tile) trigger the same sound; **Esc**
  stops everything.
- Supported formats: `.mp3`, `.wav`, `.ogg`, `.m4a`, `.flac`.
- Everything stays on your machine — the server only listens on
  `localhost`, nothing is exposed to the network.
