def test_python_utf8_smoke():
    text = "你好，火车站在哪里？"
    encoded = text.encode("utf-8")
    assert encoded.decode("utf-8") == text
