from unittest.mock import MagicMock, patch

import pandas as pd
from google.cloud.exceptions import GoogleCloudError

from src.loader import enviar_para_bigquery_idempotente


def _df_exemplo():
    return pd.DataFrame({
        "titulo": ["Titulo 1"],
        "autor": ["Autor 1"],
        "link": ["https://medium.com/artigo-1"],
        "data_publicacao": [pd.Timestamp("2024-01-01")],
        "tag_buscada": ["python"],
        "coletado_em": [pd.Timestamp.now()],
    })


@patch("src.loader.bigquery.Client")
def test_enviar_para_bigquery_idempotente_executa_stage_e_merge(mock_client_cls, monkeypatch):
    monkeypatch.setenv("ID_PROJETO", "meu-projeto")
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client

    df = _df_exemplo()
    enviar_para_bigquery_idempotente(df)

    mock_client_cls.assert_called_once()

    args_stage, kwargs_stage = mock_client.load_table_from_dataframe.call_args
    assert args_stage[0] is df
    assert args_stage[1] == "meu-projeto.medium_analytics.dados_artigos_stage"
    mock_client.load_table_from_dataframe.return_value.result.assert_called_once()

    args_query, _ = mock_client.query.call_args
    sql_executado = args_query[0]
    assert "MERGE `meu-projeto.medium_analytics.dados_artigos` T" in sql_executado
    assert "USING `meu-projeto.medium_analytics.dados_artigos_stage` S" in sql_executado
    assert "ON T.link = S.link" in sql_executado
    mock_client.query.return_value.result.assert_called_once()


@patch("src.loader.bigquery.Client")
def test_enviar_para_bigquery_idempotente_captura_googlecloud_error(mock_client_cls, monkeypatch, capsys):
    monkeypatch.setenv("ID_PROJETO", "meu-projeto")
    mock_client = MagicMock()
    mock_client.load_table_from_dataframe.side_effect = GoogleCloudError("falha simulada")
    mock_client_cls.return_value = mock_client

    enviar_para_bigquery_idempotente(_df_exemplo())

    saida = capsys.readouterr().out
    assert "Erro de integração com o Google Cloud BigQuery" in saida
    mock_client.query.assert_not_called()


@patch("src.loader.bigquery.Client")
def test_enviar_para_bigquery_idempotente_captura_erro_inesperado(mock_client_cls, monkeypatch, capsys):
    monkeypatch.setenv("ID_PROJETO", "meu-projeto")
    mock_client = MagicMock()
    mock_client.load_table_from_dataframe.side_effect = Exception("erro genérico")
    mock_client_cls.return_value = mock_client

    enviar_para_bigquery_idempotente(_df_exemplo())

    saida = capsys.readouterr().out
    assert "Erro inesperado no processo de carga" in saida
