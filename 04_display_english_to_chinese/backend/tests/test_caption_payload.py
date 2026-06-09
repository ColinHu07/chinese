from backend.captions import build_caption_payload, build_status_payload


def test_caption_payload_shape():
    payload = build_caption_payload(
        "Where is the train station?",
        "火车站在哪里？",
        mode="en_to_zh",
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


def test_caption_payload_supports_chinese_to_english_mode():
    payload = build_caption_payload(
        "你好",
        "Hello",
        mode="zh_to_en",
        created_at="2026-06-08T12:00:00Z",
    )
    assert payload["mode"] == "zh_to_en"
    assert payload["source_text"] == "你好"
    assert payload["target_text"] == "Hello"


def test_status_payload_shape():
    assert build_status_payload("connected") == {"type": "status", "status": "connected"}
