# Changelog

## 0.1.0 (2026-10-25)

- First prototype: two stopping rules (`stable_mode`, `saturation`) that turn per-frame fish counts into one tank
  count, and `python -m anyfishcount.offline` that writes `counts.csv` for R from detector boxes of recorded videos.

## Planned

- Test the rules on real tank videos (YouTube first, then Ale's videos with a known number of fish).
- Fish detector small enough for a phone (YOLO nano, ONNX), trained with the Guppy Colour training kit.
- Filming hints (blur, fish too small, tank cut off, reflections, low contrast).
- Phone web app: live video, automatic stop; later optional streaming to a PC for a bigger model.
