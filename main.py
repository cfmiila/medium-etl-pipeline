import os
import feedparser
import pandas as pd
from datetime import datetime
from google.cloud import bigquery
from dotenv import load_dotenv


load_dotenv()

path_credenciais = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if path_credenciais:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path_credenciais

def extrair_dados_medium(tag):
    url = f"https://medium.com/feed/tag/{tag}"
    feed = feedparser.parse(url)
    lista_artigos = []
    
    for entry in feed.entries:
        artigo = {
            "titulo": entry.get("title", ""),
            "autor": entry.get("author", "Anônimo"),
            "link": entry.get("link", ""),
            "data_publicacao": datetime(*entry.published_parsed[:6]), 
            "tag_buscada": tag,
            "coletado_em": datetime.now() 
        }
        lista_artigos.append(artigo)
        
    df = pd.DataFrame(lista_artigos)
    
    
    if not df.empty:
        df["data_publicacao"] = pd.to_datetime(df["data_publicacao"])
        df["coletado_em"] = pd.to_datetime(df["coletado_em"])
        
    return df

def enviar_para_bigquery(df):
    client = bigquery.Client()
    
    id_projeto = os.getenv("ID_PROJETO")
    id_tabela = f"{id_projeto}.medium_analytics.dados_artigos"
    
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND", 
    )
    
    print(f"Enviando {len(df)} linhas para o BigQuery ({id_tabela})...")
    job = client.load_table_from_dataframe(df, id_tabela, job_config=job_config)
    job.result() 
    print("Dados inseridos com sucesso!")

if __name__ == "__main__":
    print("Iniciando o pipeline...")
    df_artigos = extrair_dados_medium("python")
    
    if not df_artigos.empty:
      
        print("\n--- VISUALIZANDO OS DADOS QUE SERÃO ENVIADOS ---")
    
        print(df_artigos[["titulo", "autor", "data_publicacao"]].head(3).to_string())
        print("------------------------------------------------\n")
        # ---------------------------------------------------------
        
        enviar_para_bigquery(df_artigos)
    else:
        print("Nenhum artigo encontrado no feed.")