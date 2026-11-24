# TEST_RESULTS — news-image-20261123

Run: Tue 2026-11-24 ~17:24 WIB (10:24 UTC). Python 3.12.3, Pillow 10.2.0,
DejaVu fonts. No network used by the program.

## 1. Program run (build machine)

Command: `MAKEFUN_OUTPUT_DIR=/tmp/ni23-a python3 main.py`

```
WROTE /tmp/ni23-a/entry.png
SIZE 159764 bytes
SHA256 1fea56d75e74d03f07405128f66b75facd054305c7f12b0bac629f9f1418e943
STORIES 36 (13 picture + 23 briefs)
```

Gate limits: PNG 1024x1024, 159,764 bytes < 1 MiB cap (target < 700 KB met).
Exit code 0.

## 2. Determinism (two runs, byte-identical)

```
MAKEFUN_OUTPUT_DIR=/tmp/ni23-a python3 main.py  -> sha256 1fea56d7...
MAKEFUN_OUTPUT_DIR=/tmp/ni23-b python3 main.py  -> sha256 1fea56d7...
```

Identical sha256 `1fea56d75e74d03f07405128f66b75facd054305c7f12b0bac629f9f1418e943`
for both runs.

## 3. Clean-room run (zero-fail QA)

Fresh dir /tmp/ni23-clean holding only the package files (main.py,
README.md, LICENSE, .makefun/owner.json, entry.png). Run from that dir:

```
MAKEFUN_OUTPUT_DIR=/tmp/ni23-clean-out python3 main.py
WROTE /tmp/ni23-clean-out/entry.png
SIZE 159764 bytes
SHA256 1fea56d75e74d03f07405128f66b75facd054305c7f12b0bac629f9f1418e943
```

Same sha256 as the build machine. Exit code 0. No imports outside the
standard library + Pillow.

## 4. Secret / hardcoded-path scan

`grep -rInE "api[_-]?key|secret|token|password|sk-..."` over the package
and `grep -rInE "/home/|/Users/|C:\\"` — no matches. No credentials,
no absolute paths, no home-directory references in any shipped file.
`.makefun/owner.json` is exactly 58 bytes:
`{"wallet": "G9dDsodYieJBpsE5wBZS2drwBBRrRCF6ait6z7fhdod"}` + newline.

## 5. Kit check (local, `node cli/makefun.mjs check --kit <kit> --repo <clean> --worktree`)

- 4 passed: competition_open, snapshot (5 files, 199,920 bytes, within caps),
  license_osi (MIT), entrypoint (main.py, python3.13 accepted).
- 1 failed: transcripts_present — expected: no transcripts exist yet; the
  parent agent bundles + submits (bundle needs a git repo; git init in the
  package dir is blocked pending the user's decision).
- 14 skipped (all transcript-gate checks, no session to read yet).
- 5 at-submission checks: repo_public, repo_owner, repo_created_after_open,
  commit_in_repo, duplicate_snapshot — all handled by the parent at push +
  submit time.

## 6. Kit SHA verification

Kit tarball from https://make.fun/c/news-image-20261123/kit (8,182,262 bytes),
extracted; 11/11 file SHAs match the get_kit manifest (RULES.txt,
cli/makefun.mjs, cli/site.json, competition.yaml, harness/*, starter/*).
Bundle sha256 in manifest: 444e0a0c67da67369a24059109d7452aa035327b2d45eb1896b1da1e989cb999.

## 7. Visual check

Poster viewed at full size and downscaled: masthead date reads, 3 hero
leads (Nvidia chart, Merkury map, Hormuz diagram) legible, DAY IN NUMBERS
strip, STORIES BY REGION bar, 10 further picture stories, world map with
numbered pins 1–13 + dots 14–36, DATE CHECK and HOW TO READ boxes fit
without overflow. Fixes applied after first render: Nvidia bar-value
overlap, Hormuz label/tanker overlap, clipped mid-card labels, Europe map
pin stacking (leader lines), bottom-box overflow.

## 8. SolAPI judge (2-pass critique)

`POST /v1/responses` returned HTTP 503 on all 3 attempts (same outage as
20–23 Nov) — the gpt-6.1-sol judge pass did NOT run. No score is claimed.
Substitute: structured self-critique (see §9).

## 9. Self-critique (in place of the 503'd judge)

Strengths: 36 stories, all first reported Mon 23 Nov 2026 (UTC) with
per-day DATE CHECK exclusions (COP31 collapse + Khartoum strikes, Sun
22 Nov); hero tier has a map and two diagrams, not scenes only; region
bar + briefs grouped by region; confidence tag on every story; 160 KB,
deterministic.
Weaknesses: (a) Hormuz diagram is the weakest illustration — the tanker
reads as a small red block; (b) mid-tier art is simple icon-style, so at
thumbnail size the mid grid reads as coloured blocks (heroes carry the
thumbnail, by design); (c) hero #2 (Merkury sinking) is a CLAIM — kept
because it was the day's consensus lead everywhere, and the tag is honest;
(d) briefs are 10 px and unreadable at thumbnail — intended, stated in
HOW TO READ. No fix applied for (a)–(d): judged acceptable, and further
edits risked new defects for marginal gain.
