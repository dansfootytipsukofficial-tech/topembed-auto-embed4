#!/usr/bin/env python3
"""Check framing-related headers for TopEmbed channel URLs.

Reads out/channels.json and writes out/embed_report.json with per-channel header info.
"""
import json
import os
import sys
from urllib.parse import urlparse

import requests


def probe_url(url, timeout=10):
    result = {
        'url': url,
        'final_url': None,
        'status': None,
        'is_https': urlparse(url).scheme.lower() == 'https',
        'x_frame_options': None,
        'csp_frame_ancestors': None,
        'referrer_meta': None,
        'error': None,
    }
    headers = {'User-Agent': 'topembed-check/1.0'}
    try:
        # try HEAD first
        r = requests.head(url, headers=headers, allow_redirects=True, timeout=timeout)
        result['status'] = r.status_code
        result['final_url'] = r.url
        # check headers
        xfo = r.headers.get('X-Frame-Options') or r.headers.get('x-frame-options')
        if xfo:
            result['x_frame_options'] = xfo
        csp = r.headers.get('Content-Security-Policy') or r.headers.get('content-security-policy')
        if csp and 'frame-ancestors' in csp:
            # capture the whole header (may be long)
            result['csp_frame_ancestors'] = csp

        # some servers reject HEAD; if status looks not OK and server returned short, try GET
        if r.status_code >= 400 or r.status_code == 405:
            r2 = requests.get(url, headers=headers, allow_redirects=True, timeout=timeout, stream=True)
            result['status'] = r2.status_code
            result['final_url'] = r2.url
            # check headers again
            xfo = r2.headers.get('X-Frame-Options') or r2.headers.get('x-frame-options')
            if xfo:
                result['x_frame_options'] = xfo
            csp = r2.headers.get('Content-Security-Policy') or r2.headers.get('content-security-policy')
            if csp and 'frame-ancestors' in csp:
                result['csp_frame_ancestors'] = csp
            # try to inspect small part of body for meta referrer
            try:
                chunk = r2.raw.read(8192) or b''
                body_start = chunk.decode('utf-8', errors='ignore').lower()
                if '<meta name="referrer"' in body_start or 'meta name=\'referrer\'' in body_start:
                    result['referrer_meta'] = True
            except Exception:
                pass

    except Exception as exc:
        # fallback to GET
        try:
            r2 = requests.get(url, headers=headers, allow_redirects=True, timeout=timeout, stream=True)
            result['status'] = getattr(r2, 'status_code', None)
            result['final_url'] = getattr(r2, 'url', None)
            xfo = r2.headers.get('X-Frame-Options') or r2.headers.get('x-frame-options')
            if xfo:
                result['x_frame_options'] = xfo
            csp = r2.headers.get('Content-Security-Policy') or r2.headers.get('content-security-policy')
            if csp and 'frame-ancestors' in csp:
                result['csp_frame_ancestors'] = csp
            try:
                chunk = r2.raw.read(8192) or b''
                body_start = chunk.decode('utf-8', errors='ignore').lower()
                if '<meta name="referrer"' in body_start or "meta name='referrer'" in body_start:
                    result['referrer_meta'] = True
            except Exception:
                pass
        except Exception as exc2:
            result['error'] = str(exc2)

    return result


def main():
    base = os.path.dirname(__file__)
    cj = os.path.join(base, 'out', 'channels.json')
    if not os.path.exists(cj):
        print('Missing', cj, file=sys.stderr)
        sys.exit(2)
    with open(cj, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    channels = data.get('channels', [])
    results = []
    for i, url in enumerate(channels):
        print(f'[{i+1}/{len(channels)}] Probing', url)
        r = probe_url(url)
        results.append(r)

    out = os.path.join(base, 'out', 'embed_report.json')
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump({'results': results}, fh, indent=2)
    print('Wrote', out)


if __name__ == '__main__':
    main()
