#!/usr/bin/env python3
"""Prune channels using out/embed_report.json and write out/pruned_channels.json.

Criteria (default):
- HTTP status 200
- no X-Frame-Options header
- no CSP frame-ancestors directive
- is_https == True

Run: python prune_channels.py
"""
import json
import os
import sys


def main():
    base = os.path.dirname(__file__)
    report = os.path.join(base, 'out', 'embed_report.json')
    if not os.path.exists(report):
        print('Missing report:', report)
        sys.exit(2)
    with open(report, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    good = []
    for r in data.get('results', []):
        status = r.get('status') or 0
        xfo = r.get('x_frame_options')
        csp = r.get('csp_frame_ancestors')
        https = r.get('is_https', False)
        if status == 200 and not xfo and not csp and https:
            good.append(r.get('url'))

    out = os.path.join(base, 'out', 'pruned_channels.json')
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump({'channels': good}, fh, indent=2)
    print('Wrote', out, '(', len(good), 'channels )')


if __name__ == '__main__':
    main()
