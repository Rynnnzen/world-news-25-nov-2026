# The World in One Day — Wednesday, 25 November 2026

A single 1024x1024 newspaper-style front page that sums up the world news of
**Wednesday 25 November 2026**: all **41 stories** from **7 regions**, with
13 illustrated pictured stories and 28 listed one-line briefs.

Entry for the make.fun bounty:
**<https://make.fun/bounty/news-image-20261125>**

[![make.fun news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![make.fun rank](https://make.fun/badge/news-image-20261125/Rynnnzen/world-news-25-nov-2026/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard)
[![make.fun reward](https://make.fun/badge/news-image-20261125/Rynnnzen/world-news-25-nov-2026/reward.svg)](https://make.fun/bounty/news-image-20261125)

## What the image shows

- **Masthead** — "THE WORLD IN ONE DAY" and "Wednesday, 25 November 2026".
- **Stat strip** — 41 stories, 7 regions, 13 pictured, 28 listed, and the date.
- **Lead card** — Shenzhou-24's launch with the first Pakistani astronaut in
  orbit, with a drawn rocket illustration.
- **Twelve more pictured cards** — Europe, the Middle East, Asia, the Americas,
  Africa, Oceania and the World, each with a drawn icon, a coloured region tag,
  a headline and a one-line summary.
- **Dotted world map** — dots form the continents, and numbered pins mark the
  datelines of ten pictured stories.
- **Today's Big Five** — a compact lead-story list under the map.
- **Regional briefs** — the remaining 28 stories grouped under EUROPE, MIDDLE
  EAST, ASIA, AMERICAS, AFRICA, OCEANIA and WORLD.
- **Date check and footer** — confirming every story is dated 25 November 2026
  and that this is a news summary image, not a live news service.

All artwork is original, drawn with Pillow primitives. No photographs, no
external images and no network access are used. Every text string is measured
and shrunk or ellipsised to fit inside its box.

## Files

| File | Purpose |
| --- | --- |
| `compose.py` | Draws the infographic and writes `assets/entry.png` (Python + Pillow). |
| `assets/entry.png` | The finished 1024x1024 PNG, 164,294 bytes. |
| `main.py` | Standard-library entry point: copies the shipped image to the output directory and verifies its SHA-256. |
| `README.md` | This file. |
| `LICENSE` | MIT license. |

## Build the image

The image is already committed at `assets/entry.png`. To redraw it (requires
Pillow):

```sh
python3 compose.py
```

The drawing is deterministic, so a rerun produces byte-identical output.

## Run the entry

`main.py` uses only the Python standard library. It resolves the output
directory in this order:

1. `--output-dir PATH`
2. `$MAKEFUN_OUTPUT_DIR`
3. `/output`

```sh
python3 main.py --output-dir out
# or
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

It writes `out/entry.png` through a temporary file (`entry-*`, not a dotfile)
and an atomic rename. Before the rename it flushes, fsyncs and sets the file
mode to `0644` so the output is world-readable. It then checks that the copy's
SHA-256 matches the shipped image, and fails loudly on any mismatch or if the
shipped file is not a PNG.

SHA-256 of `assets/entry.png`:
`7f943df00a171bc752ad31d603cb1e184f4d177d1061116af25a747d096fdf32`

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Rynnnzen.
