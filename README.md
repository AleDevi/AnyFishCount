# AnyFishCount

Counts the fish in a tank from a photo or a video. Filmed with a phone, the video is read while it is taken,
and the recording stops by itself once the count no longer changes; the tool also says how to film better
(get closer, hold still, avoid reflections, change the background).

Sister tool of [Guppy Colour](https://github.com/AleDevi/fishsupercolor) (same lab, same rules: no telemetry,
models checked by SHA-256, CSV ready for R). Tuned first for guppies and zebrafish, males and females, in glass
tanks of 30–200 litres seen from the side, 10 to 200 fish; nothing species-specific is hard-coded.

Status: early prototype (0.1.0). Only the offline part exists: stopping rules tested on detector output from
videos already recorded.

## Counting videos already recorded

1. Run a fish detector on each video (2 frames per second) and write one `VIDEO_boxes.csv` per video with the
   columns `video, t_s, frame, x1, y1, x2, y2, conf` (a frame with no fish still gets one row, box fields empty).
2. `python -m anyfishcount.offline RESULTS_FOLDER --truth truth.csv` (truth.csv: `video, true_count`, optional).
3. Open `RESULTS_FOLDER/counts.csv` in R: one row per video, confidence threshold and rule.

| Column | Meaning |
| --- | --- |
| `video` | video name |
| `conf` | detector confidence threshold used |
| `rule` | stopping rule: `stable_mode` (most frequent recent count stays the same) or `saturation` (a high percentile of all counts so far stops growing) |
| `count`, `low`, `high` | tank count and plausible range |
| `seconds_used` | seconds of video needed before the rule stopped |
| `stopped` | `FALSE` if the count never settled: treat it as uncertain |
| `frames` | frames read |
| `true_count`, `error_pct` | hand count and error in % (`NA` without a truth file) |

## Why the rules differ

Fish hide behind each other and behind stones, so in any single frame some are missing and the per-frame count
rises and falls. `stable_mode` waits for that count to stop changing, so it reports roughly the typical number of
*visible* fish and undercounts. `saturation` follows a high percentile (90th) of every count seen so far: it
rises quickly while new frames reveal hidden fish and flattens once more frames add nothing.

## For developers

`pip install -e .` then `python -m pytest tests`. AGPLv3.
