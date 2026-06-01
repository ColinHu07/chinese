# Model Notes

Use local multilingual Whisper models for Mandarin-to-English translation.

Avoid English-only `.en` models and avoid `turbo` for translation.

Recommended starting points:

- `base` for live CPU tests.
- `small` for better quality if latency is acceptable.
- `medium` only on a strong machine or GPU.

Use `task="translate"` and `language="zh"` for Mandarin speech to English captions.
