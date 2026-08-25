import io
from contextlib import redirect_stdout

import streamlit as st

from src.extractor import extrair_dados_medium
from src.loader import enviar_para_bigquery_idempotente

st.set_page_config(page_title="Pipeline Medium -> BigQuery", page_icon="📰")

st.title("📰 Pipeline Medium -> BigQuery")

tag = st.text_input("Tag do Medium", value="python")
enviar_bigquery = st.checkbox("Enviar para o BigQuery", value=False)
coletar = st.button("Coletar artigos")

if coletar:
    saida_coleta = io.StringIO()
    df_artigos = None
    try:
        with redirect_stdout(saida_coleta):
            df_artigos = extrair_dados_medium(tag)
    except Exception as e:
        st.error(f"Erro inesperado ao coletar artigos: {e}")
    else:
        if "Erro crítico" in saida_coleta.getvalue():
            st.error("Falha ao coletar artigos do Medium:\n\n" + saida_coleta.getvalue())
        elif df_artigos is None or df_artigos.empty:
            st.warning(f"Nenhum artigo encontrado para a tag '{tag}'.")
        else:
            st.success(f"{len(df_artigos)} artigo(s) coletado(s) com sucesso.")

    total_artigos = len(df_artigos) if df_artigos is not None else 0
    st.metric("Artigos coletados", total_artigos)

    if df_artigos is not None and not df_artigos.empty:
        st.dataframe(df_artigos)

        if enviar_bigquery:
            saida_envio = io.StringIO()
            try:
                with redirect_stdout(saida_envio):
                    enviar_para_bigquery_idempotente(df_artigos)
            except Exception as e:
                st.error(f"Erro inesperado ao enviar para o BigQuery: {e}")
            else:
                texto_envio = saida_envio.getvalue()
                if "Erro de integração com o Google Cloud BigQuery" in texto_envio or "Erro inesperado no processo de carga" in texto_envio:
                    st.error("Falha ao enviar dados para o BigQuery:\n\n" + texto_envio)
                else:
                    st.success("Dados enviados para o BigQuery com sucesso!")
