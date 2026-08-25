import os
from dotenv import load_dotenv

from src.extractor import extrair_dados_medium
from src.loader import enviar_para_bigquery_idempotente


load_dotenv()


path_credenciais = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if path_credenciais:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path_credenciais

if __name__ == "__main__":
    print("--- INICIANDO PIPELINE DE ENGENHARIA DE DADOS ---")


    df_artigos = extrair_dados_medium("python")

    if not df_artigos.empty:
        print(f"\nArtigos capturados com sucesso. Amostra dos dados:")
        print(df_artigos[["titulo", "autor", "data_publicacao"]].head(3).to_string())
        print("-" * 50)

        enviar_para_bigquery_idempotente(df_artigos)
    else:
        print("Pipeline finalizado: Nenhum dado novo para processar.")
