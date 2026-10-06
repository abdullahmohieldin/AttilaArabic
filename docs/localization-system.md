# Localization System — Attila (Phase 2)

Date: 2026-10-06. Claims labeled VERIFIED / DOCUMENTED / INFERENCE / UNVERIFIED.
All experiments on copies; vanilla `local_en.pack` SHA256 unchanged
(`45E0F087…7F70D` before == after).

## Where localization lives — VERIFIED

- `data\local_en.pack` (PFH4, 211,301,042 B, 214 files, type `release (1)`).
- 174 `.loc` files under `text\db\*.loc` + `text\credits.xml` (175 text entries
  total). No loose `.loc` files in `data\text\` (only 3 xml files).
- File sizes range from 14 B (empty table, e.g. `agent_attributes.loc`) to
  ~725 KB (`uied_component_texts.loc`, 3119 entries).
- `local_en_shared_rome2.pack` (1.0 GB) role: UNVERIFIED (not opened yet).

## `.loc` structure — VERIFIED (own codec, byte-exact)

Layout (matches `rpfm_lib::files::loc`, DOCUMENTED, confirmed empirically):

```text
FF FE | 'LOC' | 0x00 | i32 version=1 | u32 count
per entry: u16 char-count + UTF-16LE key
           u16 char-count + UTF-16LE text
           u8 tooltip flag
```

- `source\loc.py`: decode/encode + TSV export. Exact parse
  (`consumed == total`) on all 6 files tested; **byte-identical round-trip**
  on `battles.loc`, `advice_info_texts.loc` (462 entries), `uied`,
  `factions` (2703), `start_pos_factions` (618), `technology…`,
  `multiplayer_faction_descriptions` — VERIFIED.
- Third column ("tooltip") is 0/1 in all rows seen; purpose unknown
  (DOCUMENTED as unknown by RPFM). All 4 v1-overridden rows had flag 1;
  flags preserved on write — VERIFIED.
- Inline tags observed vanilla: `[[url:…]]…[[/url]]` (advice texts),
  `[[col:…]]` family per RPFM manual (DOCUMENTED). v1 strings contain no
  tags (deliberate — see tag-order caveat below).

## Pack-type test — VERIFIED (built) / UNVERIFIED (in-game effect)

- `packfile.py` pack types: `0=boot, 1=release, 2=patch, 3=mod, 4=movie`
  (DOCUMENTED by tool). Vanilla `local_en.pack` = 1 (`release`).
- v1 test pack built as **PFH4 type `mod (3)`** via
  `packfile.py create --type 3 --version PFH4` + `add` + content verified by
  re-extract + re-decode (entry counts 3119/2703/618 intact, flags intact,
  shaped strings match) — VERIFIED.
- Expected behavior (DOCUMENTED community practice, UNVERIFIED in Attila
  until the v1 game test): `mod`-type packs are enabled per-pack in the
  launcher Mod Manager and override vanilla same-path files / same-key rows;
  `movie`-type (4) autoloads without enabling. v1 uses `mod (3)` so loading
  is explicit and reversible.
- Safety design: v1 ships **full-file copies** (only 4 rows edited), so it is
  correct under both file-replacement and key-merge engine semantics
  (INFERENCE about the two possible semantics; design covers both).

## Shaping pipeline v1 — VERIFIED at codepoint level

`source\shape.py`: protect `[[…]]` / `%s/%d` / `{n}` → `arabic_reshaper`
3.0.1 → `python-bidi` 0.6.11 `get_display(base_dir='R')` → restore tokens.

- `القاهرة` → `FE93 FEAE FEEB FE8E FED8 FEDF FE8D` (correct final/medial/
  initial forms, visual order) — VERIFIED.
- Digits stay LTR (`1200` intact), Latin runs intact (`Rome 1200` intact),
  em-dash/parens/`:`/`%` preserved, tags restored byte-identical —
  VERIFIED.
- Tag-order caveat (INFERENCE, needs engine test): bidi moves LTR tag runs,
  so in the stored visual string `[[/col]]` can precede `[[col:red]]`. If the
  engine parses tags in storage order, colors on pre-shaped tagged strings
  may break. v1 avoids tags entirely; tagged strings are a Phase 4 problem.

## Language selection — INFERENCE / UNVERIFIED

- `data\language.txt` = `EN`. RPFM docs note pre-Troy games load individual
  `.loc` files in the active language; a total-conversion-style override of
  English keys in a mod pack is the standard translation-mod mechanism
  (DOCUMENTED practice). Whether Attila merges by key across same-path files
  or replaces whole files is UNVERIFIED — v1's full-file design is safe
  either way; the in-game result decides.
