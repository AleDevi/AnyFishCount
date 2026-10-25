"""Count fish in videos already recorded, from the boxes a detector found in each frame.

python -m anyfishcount.offline RESULTS_FOLDER [--truth truth.csv]
reads every *_boxes.csv (video, t_s, frame, x1, y1, x2, y2, conf) and writes counts.csv: one row per video,
confidence threshold and stopping rule, ready for read.csv() in R.
"""
import argparse
import csv
import glob
import os
from collections import defaultdict

from .stopping import RULES

THRESHOLDS = (0.15, 0.25, 0.35)


def frame_counts(rows, conf):
    """Time (s) and number of boxes at or above `conf`, for every frame (frames with no box count 0)."""
    per = defaultdict(int)
    times = {}
    for r in rows:
        f = int(r['frame'])
        times[f] = float(r['t_s'])
        if r.get('conf') not in (None, '') and float(r['conf']) >= conf:
            per[f] += 1
    frames = sorted(times)
    return [times[f] for f in frames], [per[f] for f in frames]


def summarise(folder, truth=None):
    out = []
    for path in sorted(glob.glob(os.path.join(folder, '*_boxes.csv'))):
        with open(path, newline='', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        if not rows:
            continue
        video = rows[0]['video']
        for conf in THRESHOLDS:
            t, n = frame_counts(rows, conf)
            for name, rule in RULES.items():
                e = rule(t, n)
                true = (truth or {}).get(video)
                out.append({'video': video, 'conf': conf, 'rule': name, 'count': round(float(e.count), 1),
                            'low': round(float(e.low), 1), 'high': round(float(e.high), 1),
                            'seconds_used': round(float(e.t_stop), 1), 'stopped': 'TRUE' if e.stopped else 'FALSE',
                            'frames': len(n), 'true_count': 'NA' if true is None else true,
                            'error_pct': 'NA' if not true else round(100 * (float(e.count) - true) / true, 1)})
    return out


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('folder')
    p.add_argument('--truth', help='CSV with columns video, true_count')
    a = p.parse_args(argv)
    truth = None
    if a.truth:
        with open(a.truth, newline='', encoding='utf-8') as f:
            truth = {r['video']: float(r['true_count']) for r in csv.DictReader(f) if r['true_count'] not in ('', 'NA')}
    rows = summarise(a.folder, truth)
    with open(os.path.join(a.folder, 'counts.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ['video'])
        w.writeheader()
        w.writerows(rows)
    print(f'{len(rows)} rows -> {os.path.join(a.folder, "counts.csv")}')


if __name__ == '__main__':
    main()
