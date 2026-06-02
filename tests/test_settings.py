from mdforge.core.settings import ParserType


def test_parser_roundtrip(app_settings):
    app_settings.parser = ParserType.MINERU
    app_settings.sync()
    assert app_settings.parser == ParserType.MINERU


def test_mineru_token_persisted(app_settings):
    app_settings.mineru_token = "secret"
    app_settings.sync()
    assert app_settings.mineru_token == "secret"


def test_default_mineru_base_url(app_settings):
    assert app_settings.mineru_base_url.startswith("https://")


def test_invalid_parser_falls_back_to_markitdown(app_settings):
    app_settings._set("parser", "not-a-parser")
    assert app_settings.parser == ParserType.MARKITDOWN
