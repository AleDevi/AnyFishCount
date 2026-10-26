# Test 2026-10-25: ready-made detector on YouTube tank videos

Run offline on Ale's PC (CPU, Ryzen 5 3500U, no NVIDIA GPU). Videos stayed on that PC; only numbers are here.

- 12 videos, first 60 s each, max 720p: 8 guppy, 4 zebrafish (side view, plain, gravel, sand and planted tanks).
- Detector: YOLOE `yoloe-11l-seg.pt`, text prompt "fish", boxes only (weights checked with the Guppy Colour
  SHA-256). 2 frames per second, 1442 frames.
- Reference: fish counted by eye on 4 stills per video (48 stills). Crowded tanks are rough estimates.

## Time per frame (CPU)

| Variant | s/frame |
| --- | --- |
| image 640 px | 0.98 |
| image 1280 px | 3.71 |
| 2x2 tiles (20% overlap, NMS IoU 0.5) | 3.98 |
| 3x3 tiles | 8.74 |

## Counts per video at conf 0.25 (summary of the 4 stills)

| Video | by eye | 640 | 1280 | 2x2 | 3x3 |
| --- | --- | --- | --- | --- | --- |
| mossy_many | 21 | 9 | 18 | 21 | 32 |
| planted_many | 100 | 4 | 6 | 15 | 28 |
| slowmo | 7 | 7 | 8 | 13 | 14 |
| few_A | 5 | 1 | 0 | 1 | 2 |
| few_B | 4 | 0 | 0 | 2 | 1 |
| fry_dark | 5 | 2 | 2 | 5 | 6 |
| gold_plain | 18 | 11 | 13 | 15 | 15 |
| mixed_crowded | 270 | 2 | 4 | 17 | 29 |
| zebrafish_adults | 95 | 6 | 27 | 38 | 58 |
| zebrafish_fry | 8 | 0 | 0 | 0 | 2 |
| glofish_gravel | 4 | 0 | 1 | 3 | 3 |
| glofish_sand | 10 | 5 | 7 | 10 | 7 |

Mean absolute error against the eye counts: 640 px 75%, 1280 px 67%, 2x2 tiles 57% (best), 3x3 tiles 56% at
conf 0.35 but twice as slow.

## Conclusions

- The ready-made detector is far from the 5% target: it finds large, well-lit fish but misses small, crowded or
  camouflaged ones (50–90% missed in crowded tanks, no zebrafish fry).
- Tiles find more small fish but count a large fish twice when it crosses a tile border.
- Next: a detector fine-tuned on guppy and zebrafish tank frames, and Ale's videos with a known number of fish to
  test the stopping rules. The stopping rules cannot be judged with a detector that misses most fish.
