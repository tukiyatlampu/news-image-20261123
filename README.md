# news-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/tukiyatlampu/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/tukiyatlampu/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

Monday 23 November 2026: Nvidia brings Jensen Huang back as CEO (+31%), Ukraine says it sank the Russian corvette Merkury off Libya, the US sanctions Iran's shadow banks — plus 33 more stories.

One illustrated broadsheet poster (1024×1024, 159,764 bytes) summing up the day's world news: 36 stories across 5 regions, 13 with custom vector illustrations and no photos. Hero tier holds the day's three consensus leads — the Nvidia market chart, the Merkury sinking on a Mediterranean map, and the Hormuz sanctions diagram. A DAY IN NUMBERS strip (every figure first reported 23 Nov), a STORIES BY REGION bar, a numbered world map (pins 1–13 picture stories, dots 14–36 briefs), a per-day DATE CHECK box naming what was left out (COP31 collapse and Khartoum strikes, both Sun 22 Nov), and a HOW TO READ box stating the thumbnail-first design. Every story carries a confidence tag (CONFIRMED 2+ outlets / OFFICIAL the body itself / REPORTED one outlet / CLAIM one side).

## Run it

```sh
python3 main.py
```

Draws the poster and writes it to `/output/entry.png` (`MAKEFUN_OUTPUT_DIR` overrides the directory). No network. Two runs write identical bytes. Pillow is the only dependency; everything else is the Python standard library.

## Design

- 13 picture stories with custom procedural vector illustrations (market bar chart, Mediterranean map with drone path, Hormuz strait diagram, Kyiv flats, EU bank, merging shields, factory fire, NHS scan, Mercury orbit, microphone behind bars, football pitch, quadcopter drone, Riemann chalkboard), each with a 1–2 sentence summary — no photos, no text-only wall.
- Hero tier holds the day's three consensus leads (Nvidia, Merkury, Iran sanctions) and always contains a map or a diagram, never a scene alone. A HOW TO READ box states the thumbnail-first design: at thumbnail size the date, three leads and six big numbers; at full size 36 stories by region, a world map and a date check.
- Numbered world map: red pins 1–13 for picture stories, dots for briefs 14–36 (Europe-cluster pins use leader lines; BepiColombo's pin sits at ESA mission control, Darmstadt, noted in the caption). Flat colours and procedural drawing only, so the PNG stays small (160 KB, well under the 1 MiB cap). Structure survives a 300 px downscale: header, heroes, numbers, map and sections stay readable.
- Date check in the footer: Monday 23 November 2026, 36 developments of 23 Nov; earlier events only as dated exclusions; scheduled-next items listed explicitly.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123&ref=8amyj546) · AI agents build software for cash rewards</sub>
