import os
from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError


def enviar_para_bigquery_idempotente(df):
    """Envia os dados para o BigQuery garantindo que não haverá duplicidade via MERGE."""
    client = bigquery.Client()
    id_projeto = os.getenv("ID_PROJETO")

    #  (Tabela de Destino Definitiva e Tabela de Stage Temporária)
    dataset_id = "medium_analytics"
    tabela_final = f"{id_projeto}.{dataset_id}.dados_artigos"
    tabela_stage = f"{id_projeto}.{dataset_id}.dados_artigos_stage"

    try:
        # 1. Carrega os dados novos na tabela de STAGE (sobrescrevendo o stage anterior)
        config_stage = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
        print(f"Enviando {len(df)} linhas para a tabela de Stage ({tabela_stage})...")

        job_stage = client.load_table_from_dataframe(df, tabela_stage, job_config=config_stage)
        job_stage.result()  # Aguarda a conclusão

        # 2. Executa a query de MERGE para mover os dados do Stage para a tabela Final sem duplicar
        # O link do artigo usei como Chave Primária
        sql_merge = f"""
            MERGE `{tabela_final}` T
            USING `{tabela_stage}` S
            ON T.link = S.link
            WHEN NOT MATCHED THEN
              INSERT (titulo, autor, link, data_publicacao, tag_buscada, coletado_em)
              VALUES (S.titulo, S.autor, S.link, S.data_publicacao, S.tag_buscada, S.coletado_em);
        """

        print("Executando comando MERGE para garantir a idempotência e evitar duplicados...")
        query_job = client.query(sql_merge)
        query_job.result()

        print("Dados integrados com sucesso e sem duplicidades!")

    except GoogleCloudError as gcp_err:
        print(f"Erro de integração com o Google Cloud BigQuery: {gcp_err}")
    except Exception as e:
        print(f"Erro inesperado no processo de carga: {e}")
