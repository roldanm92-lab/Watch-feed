#!/usr/bin/env python3
"""Build index.html (a static, watch-friendly page) from feed.json.

feed.json format:
{
  "updated": "2026-10-19T07:40:00-04:00",
  "tweets": [
    {"name": "Display Name", "handle": "user", "time": "2h",
     "text": "Tweet text", "url": "https://x.com/user/status/123",
     "image": "https://pbs.twimg.com/... (optional)",
     "replies": 1, "reposts": 2, "likes": 3}
  ]
}
The page is plain HTML with no JavaScript, so it renders reliably in the
Apple Watch's built-in web view.
"""
import html
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent


def esc(s):
    return html.escape(str(s or ""), quote=True)


def fmt_count(n):
    try:
        n = int(n)
    except (TypeError, ValueError):
        return ""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M".replace(".0M", "M")
    if n >= 1_000:
        return f"{n / 1_000:.1f}K".replace(".0K", "K")
    return str(n)


def render_tweet(t):
    body = esc(t.get("text")).replace("\n", "<br>")
    img = ""
    if t.get("image"):
        img = f'<img src="{esc(t["image"])}" alt="" loading="lazy">'
    stats = []
    for key, label in (("replies", "💬"), ("reposts", "🔁"), ("likes", "♥")):
        c = fmt_count(t.get(key))
        if c:
            stats.append(f"<span>{label} {c}</span>")
    stats_html = f'<div class="stats">{"".join(stats)}</div>' if stats else ""
    name = esc(t.get("name") or t.get("handle"))
    meta = f'@{esc(t.get("handle"))} · {esc(t.get("time"))}'
    inner = (
        f'<div class="who"><b>{name}</b></div>'
        f'<div class="meta">{meta}</div>'
        f'<p>{body}</p>{img}{stats_html}'
    )
    if t.get("url"):
        return f'<a class="tw" href="{esc(t["url"])}">{inner}</a>'
    return f'<div class="tw">{inner}</div>'


def main():
    data = json.loads((ROOT / "feed.json").read_text())
    tweets = data.get("tweets", [])
    updated = data.get("updated", "")
    try:
        updated_label = datetime.fromisoformat(updated).strftime("%b %-d, %-I:%M %p")
    except ValueError:
        updated_label = updated
    items = "\n".join(render_tweet(t) for t in tweets) or '<p class="empty">No tweets yet.</p>'
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="disabled-adaptations" content="watch">
<title>Feed</title>
<style>
  html, body {{ margin: 0; padding: 0; background: #000; color: #e7e9ea; }}
  body {{ font: 15px/1.3 -apple-system, system-ui, sans-serif; padding: 4px 6px 24px; }}
  h1 {{ font-size: 13px; color: #71767b; font-weight: 600; margin: 4px 2px 8px; text-align: center; }}
  .tw {{ display: block; color: inherit; text-decoration: none; background: #16181c;
         border-radius: 14px; padding: 9px 10px; margin-bottom: 7px; }}
  .who {{ font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .meta {{ font-size: 11px; color: #71767b; margin-top: 1px; }}
  p {{ margin: 5px 0 0; word-wrap: break-word; overflow-wrap: anywhere; }}
  img {{ display: block; width: 100%; border-radius: 10px; margin-top: 6px; }}
  .stats {{ font-size: 11px; color: #71767b; margin-top: 6px; }}
  .stats span {{ margin-right: 8px; }}
  .empty, .foot {{ color: #71767b; text-align: center; font-size: 12px; }}
</style>
</head>
<body>
<h1>Feed · {esc(updated_label)}</h1>
{items}
<p class="foot">{len(tweets)} posts</p>
</body>
</html>
"""
    (ROOT / "index.html").write_text(page)
    print(f"Built index.html with {len(tweets)} tweets")


if __name__ == "__main__":
    main()
