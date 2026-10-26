"""When to stop counting: from the fish seen in each video frame to one count for the tank.

In a real tank the per-frame count goes up and down all the time (fish hide behind each other, behind stones,
leave the view), so a single frame undercounts. Each rule reads the counts in time order and says when more
frames would no longer change the answer.
"""
from dataclasses import dataclass

import numpy as np


@dataclass
class Estimate:
    count: float        # the tank count
    low: float          # plausible range
    high: float
    t_stop: float       # seconds of video used
    stopped: bool       # False = never settled before the end or max_time: the count is uncertain
    rule: str


def _tol(value, rel):
    return max(1.0, rel * value)


def stable_mode(t, n, window=4.0, hold=3.0, rel=0.05, min_time=5.0, max_time=60.0):
    """Stop when the most frequent count of the last `window` seconds stays the same for `hold` seconds."""
    t, n = np.asarray(t, float), np.asarray(n, float)
    since, last = None, None
    for i, ti in enumerate(t):
        if ti > max_time:
            break
        w = n[(t > ti - window) & (t <= ti)]
        vals, freq = np.unique(w, return_counts=True)
        mode = vals[np.argmax(freq)]
        tight = np.percentile(w, 90) - np.percentile(w, 10) <= 2 * _tol(mode, rel)
        if tight and last is not None and abs(mode - last) <= _tol(mode, rel):
            since = ti if since is None else since
        else:
            since = None
        last = mode
        if since is not None and ti - since >= hold and ti >= min_time:
            return Estimate(mode, np.percentile(w, 10), np.percentile(w, 90), ti, True, 'stable_mode')
    i = np.searchsorted(t, min(t[-1], max_time), side='right')
    w = n[(t > t[i - 1] - window) & (t <= t[i - 1])]
    vals, freq = np.unique(w, return_counts=True)
    return Estimate(vals[np.argmax(freq)], np.percentile(w, 10), np.percentile(w, 90), t[i - 1], False, 'stable_mode')


def saturation(t, n, q=90.0, hold=5.0, rel=0.03, min_time=5.0, max_time=60.0):
    """Stop when a high percentile of all counts so far stops growing for `hold` seconds.

    A high percentile, not the maximum: the maximum also catches the rare frame with a reflection counted as a
    fish, and it never stops rising on a long video.
    """
    t, n = np.asarray(t, float), np.asarray(n, float)
    est = np.array([np.percentile(n[:i + 1], q) for i in range(len(n))])
    for i, ti in enumerate(t):
        if ti > max_time:
            break
        j = np.searchsorted(t, ti - hold)
        if ti >= min_time and ti - t[0] >= hold and est[i] - est[j] <= _tol(est[i], rel):
            return Estimate(est[i], np.percentile(n[:i + 1], 50), np.max(n[:i + 1]), ti, True, 'saturation')
    i = np.searchsorted(t, min(t[-1], max_time), side='right') - 1
    return Estimate(est[i], np.percentile(n[:i + 1], 50), np.max(n[:i + 1]), t[i], False, 'saturation')


RULES = {'stable_mode': stable_mode, 'saturation': saturation}
