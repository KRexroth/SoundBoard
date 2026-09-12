# Friend Group Soundboard

A soundboard with no build step and no server: `index.html` asks GitHub
directly, on every page load, "what's in the `Sounds` folder right now?"
and turns the answer into a grid of clickable tiles. Add a file to
`Sounds` on GitHub, refresh the page, it's a tile — nothing else to touch.

It's hosted as a GitHub Pages site, so there's one URL anyone can open —
no downloading, no Python, no local server.

## How it works

`index.html` calls GitHub's public API —
`api.github.com/repos/KRexroth/SoundBoard/contents/Sounds` — which lists
whatever files are in that folder. For each audio file it gets back, it
builds a tile named after the filename (`air-horn.mp3` → "Air Horn") and
points it at that file's direct GitHub URL. Clicking a tile just plays
that URL with a normal HTML `<audio>` element — it plays on whichever
device has the page open.

Because this reads the *public* GitHub API, the repo has to be public for
it to work (see below for why that's fine here).

## Managing sounds

You (Kevin) add and remove files directly in the `Sounds` folder on
github.com — via **Add file → Upload files**, dragging files onto that
folder, or however else you'd normally edit files on GitHub. There's no
upload feature in the page itself by design — this keeps "who can add
sounds" simply "whoever has push access to the repo," which is you.

## About the repo being public

A GitHub Pages site is always publicly reachable by its URL, *regardless*
of whether the source repo is public or private — private-repo Pages is a
paid-plan feature, and even then the published page itself still isn't
access-restricted. So making the repo public doesn't give up anything
here: it just means anyone can view the code and the sound files (fine for
a set of fun clips), while push access — actually adding or changing
files — is still limited to you and anyone you explicitly add as a
collaborator, independent of the public/private setting.

## Setting up GitHub Pages (one-time)

1. Repo **Settings → General → Danger Zone → Change visibility → Public**.
2. Repo **Settings → Pages → Build and deployment → Source: Deploy from a
   branch → Branch: `main`, folder `/(root)` → Save**.
3. After a minute, GitHub shows the live URL — something like
   `https://krexroth.github.io/SoundBoard/`. That's the link to share.

## Notes

- Supported formats: `.mp3`, `.wav`, `.ogg`, `.m4a`, `.flac`.
- Sounds can overlap — clicking a second tile doesn't cut off the first.
- Keyboard shortcuts (shown on each tile) trigger the same sound; **Esc**
  stops everything.
- GitHub's public API is rate-limited to 60 requests/hour per visitor IP
  with no login — plenty for casual use, but if a lot of people are
  mashing Refresh in a short window, loads can start failing until the
  hour rolls over.

## Roadmap: making it play in the actual Discord call

This is the bigger step, whenever you're ready for it. The short version:

A browser tab can only make sound come out of *your* speakers — nothing
here can inject audio into someone else's app, including Discord. To have
a click be heard by the whole voice channel, something needs to actually
**join the call as a participant** and stream the audio in. That's a
Discord bot, and it needs:

- A bot application registered in the
  [Discord Developer Portal](https://discord.com/developers/applications),
  invited to your server with permission to connect/speak in voice
  channels.
- A small always-running Node.js process (`discord.js` +
  `@discordjs/voice`, plus `ffmpeg` for decoding) that joins your voice
  channel and plays a file from the same `Sounds` folder on command (a
  slash command like `/play ding`, or this page calling an API the bot
  exposes).
- Somewhere for that process to run continuously — your own PC while
  everyone's in the call, a Raspberry Pi, or a cheap/free host (Railway,
  Fly.io, a small VPS).

Since the sound files already live in this repo's `Sounds` folder, the
bot can read from the exact same place this page does — no rework needed
there when you're ready to build it.
