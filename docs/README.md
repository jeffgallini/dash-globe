# GitHub Pages source

This directory is published to **https://jeffgallini.github.io/dash-globe/** by
[`.github/workflows/docs.yml`](../.github/workflows/docs.yml).

## Local preview

Open `docs/index.html` in a browser, or:

```bash
python -m http.server 8080 --directory docs
```

## Refresh example media

With the gallery running (`python dash_globe/usage.py`):

```bash
python script/capture_docs_media.py
```

Enable GitHub Pages in the repo settings: **Settings → Pages → Source = GitHub Actions**.
