# GitHub Pages source

This directory is published to **https://jeffgallini.github.io/dash-globe/** by
[`.github/workflows/docs.yml`](../.github/workflows/docs.yml).

## Pages

| Path | Purpose |
| --- | --- |
| `index.html` / `index.md` | Home |
| `getting-started.html` / `getting-started.md` | Quick start |
| `api.html` / `api.md` | Python API reference |
| `examples.html` / `examples.md` | Example gallery |
| `llms.txt` | LLM-oriented site map ([llms.txt spec](https://llmstxt.org/)) |

Markdown siblings and `llms.txt` are for agents; HTML pages include
`rel="alternate"` / `rel="describedby"` links to them.

## Local preview

Open `docs/index.html` in a browser, or:

```bash
python -m http.server 8080 --directory docs
```

Then visit:

- http://127.0.0.1:8080/
- http://127.0.0.1:8080/api.html
- http://127.0.0.1:8080/llms.txt

## Refresh example media

With the gallery running (`python dash_globe/usage.py`):

```bash
python script/capture_docs_media.py
```

Enable GitHub Pages in the repo settings: **Settings → Pages → Source = GitHub Actions**.
