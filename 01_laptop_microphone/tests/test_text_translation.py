from text_translation import BaiduConfig, BaiduTranslator


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, payload):
        self.payload = payload
        self.last_request = None

    def post(self, url, data, timeout):
        self.last_request = {"url": url, "data": data, "timeout": timeout}
        return FakeResponse(self.payload)


def test_baidu_signature_matches_documented_shape():
    translator = BaiduTranslator(BaiduConfig(app_id="2015063000000001", secret_key="12345678"))
    assert translator.sign("apple", "1435660288") == "f89f9594663708c1605f3d736d01d2d4"


def test_baidu_translate_posts_signed_request():
    session = FakeSession({"trans_result": [{"src": "你好", "dst": "Hello"}]})
    config = BaiduConfig(app_id="app", secret_key="secret", timeout_seconds=3)
    translator = BaiduTranslator(config, session=session)

    assert translator.translate("你好", source_lang="zh", target_lang="en") == "Hello"
    assert session.last_request["url"] == config.endpoint
    assert session.last_request["timeout"] == 3
    assert session.last_request["data"]["q"] == "你好"
    assert session.last_request["data"]["from"] == "zh"
    assert session.last_request["data"]["to"] == "en"
    assert session.last_request["data"]["appid"] == "app"
    assert session.last_request["data"]["sign"]
