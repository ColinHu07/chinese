from display_bridge import DisplayCaption, DisplayCaptionClient


class FakeResponse:
    def raise_for_status(self):
        return None


class FakeSession:
    def __init__(self):
        self.last_request = None

    def post(self, url, json, timeout):
        self.last_request = {"url": url, "json": json, "timeout": timeout}
        return FakeResponse()


def test_display_caption_client_posts_payload():
    session = FakeSession()
    client = DisplayCaptionClient("http://localhost:8000/caption", timeout_seconds=1.5, session=session)

    client.post(
        DisplayCaption(
            mode="zh_to_en",
            source_text="你好",
            target_text="Hello",
            latency_ms=1234,
        )
    )

    assert session.last_request == {
        "url": "http://localhost:8000/caption",
        "json": {
            "mode": "zh_to_en",
            "source_text": "你好",
            "target_text": "Hello",
            "is_final": True,
            "latency_ms": 1234,
        },
        "timeout": 1.5,
    }
