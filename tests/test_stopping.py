import csv

import numpy as np

from anyfishcount import offline
from anyfishcount.stopping import saturation, stable_mode


def tank(true=40, seconds=60, fps=2, seed=0, hidden=0.15):
    """Per-frame counts of a tank with `true` fish: each fish is hidden in a frame with probability ~`hidden`,
    in slow waves (fish swim behind stones in groups), plus a rare false fish."""
    rng = np.random.default_rng(seed)
    t = np.arange(0, seconds, 1 / fps)
    wave = hidden * (1 + np.sin(2 * np.pi * t / 7)) / 2 * 2
    n = rng.binomial(true, 1 - np.clip(wave, 0, 0.9)) + rng.binomial(1, 0.05, t.size)
    return t, n


def test_saturation_reaches_the_true_count_despite_hidden_fish():
    errs = []
    for seed in range(10):
        t, n = tank(seed=seed)
        e = saturation(t, n)
        assert e.stopped and e.t_stop < 60
        errs.append(abs(e.count - 40) / 40)
    assert np.mean(errs) <= 0.05


def test_stable_mode_undercounts_when_fish_hide():
    t, n = tank(seed=1, hidden=0.3)
    assert stable_mode(t, n).count < saturation(t, n).count


def test_constant_count_stops_early():
    t = np.arange(0, 60, 0.5)
    n = np.full(t.size, 12)
    for rule in (stable_mode, saturation):
        e = rule(t, n)
        assert e.stopped and e.count == 12 and e.t_stop <= 6


def test_never_settles_says_so():
    t = np.arange(0, 30, 0.5)
    n = (t * 3).astype(int)          # keeps rising: fish still entering the view
    for rule in (stable_mode, saturation):
        assert not rule(t, n).stopped


def test_offline_writes_one_row_per_video_threshold_rule(tmp_path):
    with open(tmp_path / 'v1_boxes.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['video', 't_s', 'frame', 'x1', 'y1', 'x2', 'y2', 'conf'])
        for i in range(40):
            w.writerow(['v1', i / 2, i, '', '', '', '', ''])
            for k in range(5):
                w.writerow(['v1', i / 2, i, 0, 0, 1, 1, 0.5])
    offline.main([str(tmp_path)])
    with open(tmp_path / 'counts.csv', newline='') as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == len(offline.THRESHOLDS) * 2
    assert all(float(r['count']) == 5 for r in rows) and rows[0]['true_count'] == 'NA'
