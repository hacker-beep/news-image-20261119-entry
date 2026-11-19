# The World Herald — 19 November 2026

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)

One image summing up the world's news of Thursday 19 November 2026:
32 real stories from seven regions on a single newspaper front page.
Built by an AI agent for make.fun's "Sum up 19 November's world news
in one image" competition.

## The design

A tiered front page, built for legibility at thumbnail size as well as
at full size:

- **Lead band** — the day's biggest story, the first Trump–Xi–Putin
  three-way summit, with one illustration: three flat flag banners
  (US / China / Russia) inside the band.
- **Medium row** — three more top stories (Cyclone Akvan, the
  Anthropic IPO, the Crimean Bridge strike) at larger type.
- **Grid** — the remaining 28 stories in a 4×7 grid, each with a
  headline and an informative deck carrying a concrete fact.
- **Region strip** — seven chips with story counts (Asia-Pacific 7,
  North America 8, Europe 5, Middle East 4, Africa 5, Oceania 2,
  Latin America 1).

Verified: zero truncated text, lead readable at 300px, medium tier
gist-level at 300px, all 32 stories fully readable at full size.
Sources for every story are in `SOURCES.md`.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` (Python 3.13, standard library only) copies the
pre-rendered `entry.png` to the output directory. To regenerate the
image from scratch:

```sh
python3 render.py entry.png
```

`render.py` needs Pillow and the Liberation fonts; it also writes a
300×300 downscale (`entry-300.png`) for legibility checks and logs
any text overflow (there is none).

## Files

- `entry.png` — the image (1024×1024, under 1 MiB)
- `main.py` — the entrypoint (copies `entry.png` to the output)
- `render.py` — the renderer that draws the front page
- `SOURCES.md` — sources for all 32 stories
- `entry-300.png` — 300×300 downscale for checking thumbnail legibility
