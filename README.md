# Mufime

A simple, bold, colorful landing page for Mufime with links to YouTube videos and socials. Pure static HTML/CSS/JS — no build step needed.

## Before you deploy

Open `index.html` and replace the placeholders:

- `REPLACE_WITH_VIDEO_ID_1` … `_4` — the YouTube video ID from each video's URL (the part after `watch?v=`). Update the thumbnail `src`, the card link `href`, the title, and the description for each.
- `REPLACE_WITH_CHANNEL_HANDLE` — your YouTube channel handle (e.g. `@mufime`), used in both the "Subscribe" and "YouTube Channel" buttons.
- `REPLACE_WITH_HANDLE` — your Instagram handle (or delete that link block if you don't want it).
- The `mailto:` link already points to mustafaworks786@gmail.com — change it if needed.

## Deploy to Vercel

**Option A — Vercel CLI**
```bash
npm i -g vercel
cd mufime-site
vercel
```
Follow the prompts (link/create a project, accept defaults). Vercel will detect this as a static site automatically.

**Option B — GitHub + Vercel dashboard**
1. Push this folder to a new GitHub repo.
2. Go to https://vercel.com/new and import the repo.
3. Leave all build settings blank/default (no framework, no build command) — Vercel will serve `index.html` directly.
4. Click Deploy.

That's it — no dependencies, no build step.
