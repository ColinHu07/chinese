# WebSocket Protocol

## Client -> Server

Binary frames contain mono PCM audio.

Defaults:

- sample rate: `16000`
- format: little-endian signed `int16`
- channels: `1`

The server also accepts JSON text pings:

```json
{"type": "ping"}
```

## Server -> Client

Ready message:

```json
{
  "type": "ready",
  "client_id": "...",
  "sample_rate": 16000,
  "pcm_format": "int16"
}
```

Caption message:

```json
{
  "type": "caption",
  "client_id": "...",
  "chunk_id": 4,
  "text": "How much does this cost?",
  "raw_text": "How much does this cost?",
  "inference_seconds": 1.9
}
```
