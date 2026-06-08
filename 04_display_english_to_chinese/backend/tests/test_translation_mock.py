from backend.translation.mock_translator import MockTranslator


def test_mock_translator_known_phrase():
    translator = MockTranslator()
    assert translator.translate("Where is the train station?") == "火车站在哪里？"


def test_mock_translator_unknown_phrase_marks_output():
    translator = MockTranslator()
    assert translator.translate("This is a new phrase.") == "[mock zh] This is a new phrase."
