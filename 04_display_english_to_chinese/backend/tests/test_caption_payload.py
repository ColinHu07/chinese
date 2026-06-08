from backend.captions import build_caption_payload, build_status_payload


def test_caption_payload_shape():
    payload = build_caption_payload(
        "Where is the train station?",
        "火车站在哪里？",
        created_at="2026-06-08T12:00:00Z",
    )
    assert payload == {
        "type": "caption",
        "mode": "en_to_zh",
        "source_text": "Where is the train station?",
        "target_text": "火车站在哪里？",
        "is_final": True,
        "latency_ms": 0,
        "created_at": "2026-06-08T12:00:00Z",
    }


def test_status_payload_shape():
    assert build_status_payload("connected") == {"type": "status", "status": "connected"}
