# Thalassia Passport — make.fun entry

`main.py` draws, fully offline, one open passport spread for the invented
island Republic of Thalassia (1024 x 1024 PNG, under 1 MiB) to
`/output/entry.png`.

- Left page: data page — portrait, personal details, and a machine-readable
  zone with correct ICAO check digits.
- Right page: a Veldoria visa sticker and arrival/departure stamps from
  three neighbouring states (Veldoria, Korvath, Isle of Seren) telling one
  consistent journey, 19 JUL – 05 SEP 2024, all after the passport's
  02 JUN 2024 issue date — plus a fee stamp and the island republic's
  return-if-found note.

Run: `python3 main.py` (Python 3.13, Pillow; bundled DejaVu fonts are used
when present, with a stdlib-only fallback if Pillow is unavailable).

Entry for the make.fun bounty "The Passport Page of a Country That Isn't
There" (the-passport-page-of-a-countr-2-20261121-0318).
