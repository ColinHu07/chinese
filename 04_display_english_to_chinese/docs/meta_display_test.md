# Meta Ray-Ban Display Test Checklist

## Static Glyph Test

1. Deploy `display-webapp/` to a public HTTPS URL.
2. Enable Developer Mode for the glasses in the Meta AI app.
3. Add the deployed URL under Display Glasses settings -> App connections -> Web apps.
4. Open the app on the glasses.
5. Cycle through captions with left/right input.

Pass criteria:

- `你好` renders.
- `谢谢` renders.
- `火车站在哪里？` renders.
- `请问洗手间在哪里？` renders.
- `我想点一杯咖啡。` renders.
- `今天下午三点开会。` renders.
- No text appears as missing-glyph boxes.
- No horizontal overflow is visible.

## Live Caption Injection Test

For deployed glasses testing, the web app must use a public `wss://` backend or relay. A public `https://` app should not depend on `ws://localhost`.

Desktop-only test:

```bash
curl -X POST http://localhost:8000/test-caption \
  -H "Content-Type: application/json" \
  -d '{"source_text":"Where is the train station?","target_text":"火车站在哪里？"}'
```

## Out of Scope

This web app does not capture microphone audio. Audio capture belongs in a backend or native mobile app.
