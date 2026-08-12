# Deploying the free version (real users, zero cost)

This version (`free_app.py`) has no API calls at all — extraction runs on free
OCR (Tesseract) + regex, and the "plain English" verdict is rule-based text,
not AI-generated. Nothing here costs money, including hosting.

## 1. Push to GitHub
Create a new repo (can be public) and push these files:
```
free_app.py
free_extract.py
astro_core.py
gun_milan.py
requirements_free.txt   -> rename to requirements.txt for the deploy repo
packages.txt
```

## 2. Deploy on Streamlit Community Cloud (free, no credit card)
1. Go to https://share.streamlit.io and sign in with GitHub.
2. Click "New app", pick your repo, branch, and set the main file to `free_app.py`.
3. Deploy. First build takes a few minutes (installs Tesseract via `packages.txt`).
4. You'll get a public URL like `yourapp.streamlit.app` — this is what you share
   with real people to test.

## Known limits of the free tier (worth knowing before you share it widely)
- **Sleeps after inactivity.** If nobody visits for a while, the app goes to
  sleep and the next visitor waits ~30-60 seconds for it to wake up. Fine for
  early testing, mention it to testers so they don't think it's broken.
- **Shared compute** — fine for a handful of testers, not built for real scale.
  If this starts getting real traffic, that's a good problem — move to Cloud Run.
- **Nominatim (free geocoding) rate limit** is roughly 1 request/second. If
  several people test at the exact same moment, some place lookups might fail
  momentarily — not a bug, just the free geocoder being polite to itself.

## What "free" extraction actually means for your testers
OCR + regex works well on:
- Clean typed screenshots (a form, a note-taking app, WhatsApp text messages)
- Reasonably structured pasted text ("DOB: ...", "Name: ...", etc.)

It's shakier on:
- Handwritten photos
- Screenshots with lots of unrelated text/clutter around the birth details
- Very unusual phrasing

That's fine for testing — the app always shows the extracted fields as editable
text boxes before matching, so a wrong guess just means the tester corrects it
manually, not a broken result.
