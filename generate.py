#!/usr/bin/env python3
"""Generate a lightweight static page from topembed API.

Usage: python generate.py --output out --limit 120
"""
import argparse
import json
import os
import re
import sys
from urllib.parse import unquote

import requests

API_URL = "https://topembed.pw/api.php?format=json"

HTML_HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="referrer" content="no-referrer">
<title>TopEmbed — Channels</title>
<style>
body{font-family:Arial,Helvetica,sans-serif;margin:0;background:#111;color:#eee}
.header{padding:18px;text-align:center;background:#0b0b0b}
.container{display:flex;flex-wrap:wrap;padding:10px;gap:8px}
.card{background:#141414;border:1px solid #222;border-radius:6px;flex:1 1 300px;min-width:260px;max-width:420px;padding:8px;box-sizing:border-box}
.card button{width:100%;padding:10px;border-radius:4px;border:0;background:#0a84ff;color:white;font-weight:600}
.title{font-size:14px;margin:6px 0}
.player{position:sticky;top:0;background:#000;padding:8px}
.player iframe{width:100%;height:480px;border:0}
.small{font-size:12px;color:#bbb}
</style>
</head>
<body>
<div class="header"><h1 style="margin:.2em 0">TopEmbed — Channels</h1>
<p class="small">Click a tile to open the stream in the player. Lazy-loads a single iframe to reduce browser load.</p>
</div>
<div class="player" id="player">
<p class="small" style="color:#ccc">No channel loaded. Click a tile to play.</p>
</div>
<div class="container">
"""

HTML_TAIL = """
</div>
<script>
function loadChannel(src, label){
  const p = document.getElementById('player');
  p.innerHTML = '';
  const iframe = document.createElement('iframe');
  iframe.src = src;
  iframe.setAttribute('allow','autoplay; fullscreen');
  iframe.allowFullscreen = true;
  iframe.loading = 'eager';
  p.appendChild(iframe);
  // scroll player into view
  iframe.scrollIntoView({behavior:'smooth'});
}
</script>
</body>
</html>
"""


def safe_channel_label(url):
    # url examples: https:\/\/topembed.pw\/channel\/ESPN2[USA]
    # we remove protocol and domain then decode
    try:
        if url.startswith('https'):
            # strip escapes
            clean = url.replace('\\/', '/')
            # get last path segment
            label = clean.split('/')[-1]
            label = unquote(label)
            # replace + or %20
            label = label.replace('+',' ').replace('%20',' ')
            return label
    except Exception:
        pass
    return url


def fetch_channels(limit=200):
    print('Fetching API...', API_URL)
    r = requests.get(API_URL, timeout=15)
    r.raise_for_status()
    data = r.json()
    channels = []
    seen = set()
    events = data.get('events', {})
    for day, items in events.items():
        for ev in items:
            for c in ev.get('channels', []) or []:
                # API returns escaped slashes; unescape
                src = c.replace('\\/', '/')
                if src not in seen:
                    seen.add(src)
                    channels.append(src)
                    if len(channels) >= limit:
                        return channels
    return channels


def load_channels_from_file(path, limit=200):
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        # accept either {'channels': [...]} or a plain list
        if isinstance(data, dict) and 'channels' in data:
            chans = data['channels']
        elif isinstance(data, list):
            chans = data
        else:
            chans = []
        # preserve order, apply limit
        return chans[:limit]
    except Exception:
        return []


def build_html(channels, outpath):
    print('Building HTML with', len(channels), 'channels')
    parts = [HTML_HEAD]

    for src in channels:
        label = safe_channel_label(src)
        # escape for HTML attributes
        escaped_src = src.replace('"', '&quot;')
        card = f"""
<div class="card">
  <div class="title">{label}</div>
  <div class="small">Source: <a href="{escaped_src}" target="_blank" rel="noopener noreferrer" style="color:#7fe0ff">Open</a></div>
  <div style="margin-top:8px"><button onclick="loadChannel('{escaped_src}','{label}')">Play</button></div>
</div>
"""
        parts.append(card)

    parts.append(HTML_TAIL)
    html = ''.join(parts)
    os.makedirs(outpath, exist_ok=True)
    # write HTML
    path = os.path.join(outpath, 'index.html')
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(html)
    # also write a machine-readable channels list for debugging/consumers
    try:
        cj = os.path.join(outpath, 'channels.json')
        with open(cj, 'w', encoding='utf-8') as fh:
            json.dump({'channels': channels}, fh, indent=2)
        print('Wrote', cj)
    except Exception:
        pass

    print('Wrote', path)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--output', '-o', default='out', help='output directory')
    p.add_argument('--limit', '-n', type=int, default=120, help='max channels to include')
    p.add_argument('--input-channels', '-i', help='JSON file with channels list (overrides API fetch)')
    args = p.parse_args()

    if args.input_channels:
        chans = load_channels_from_file(args.input_channels, limit=args.limit)
    else:
        chans = fetch_channels(limit=args.limit)
    build_html(chans, args.output)
