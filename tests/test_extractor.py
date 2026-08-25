from unittest.mock import patch

import feedparser
import pandas as pd

from src.extractor import extrair_dados_medium


def _fake_entry(**kwargs):
    return feedparser.FeedParserDict(**kwargs)


class _FakeFeed:
    def __init__(self, entries):
        self.entries = entries


@patch("src.extractor.feedparser.parse")
def test_extrair_dados_medium_retorna_dataframe_preenchido(mock_parse):
    entry = _fake_entry(
        title="Titulo 1",
        author="Autor 1",
        link="https://medium.com/artigo-1",
        published_parsed=(2024, 1, 1, 12, 0, 0, 0, 1, 0),
    )
    mock_parse.return_value = _FakeFeed([entry])

    df = extrair_dados_medium("python")

    mock_parse.assert_called_once_with("https://medium.com/feed/tag/python")
    assert list(df.columns) == [
        "titulo", "autor", "link", "data_publicacao", "tag_buscada", "coletado_em",
    ]
    assert len(df) == 1
    linha = df.iloc[0]
    assert linha["titulo"] == "Titulo 1"
    assert linha["autor"] == "Autor 1"
    assert linha["link"] == "https://medium.com/artigo-1"
    assert linha["tag_buscada"] == "python"
    assert linha["data_publicacao"] == pd.Timestamp(2024, 1, 1, 12, 0, 0)
    assert pd.notnull(linha["coletado_em"])


@patch("src.extractor.feedparser.parse")
def test_extrair_dados_medium_usa_valores_padrao_quando_campos_ausentes(mock_parse):
    entry = _fake_entry(link="https://medium.com/artigo-2")
    mock_parse.return_value = _FakeFeed([entry])

    df = extrair_dados_medium("python")

    linha = df.iloc[0]
    assert linha["titulo"] == ""
    assert linha["autor"] == "Anônimo"
    assert linha["data_publicacao"] is None or pd.isnull(linha["data_publicacao"])


@patch("src.extractor.feedparser.parse")
def test_extrair_dados_medium_sem_entradas_retorna_dataframe_vazio(mock_parse):
    mock_parse.return_value = _FakeFeed([])

    df = extrair_dados_medium("python")

    assert isinstance(df, pd.DataFrame)
    assert df.empty


@patch("src.extractor.feedparser.parse")
def test_extrair_dados_medium_em_caso_de_erro_retorna_dataframe_vazio(mock_parse):
    mock_parse.side_effect = Exception("falha de rede simulada")

    df = extrair_dados_medium("python")

    assert isinstance(df, pd.DataFrame)
    assert df.empty
