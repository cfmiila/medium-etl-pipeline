import feedparser
import pandas as pd
from datetime import datetime


def extrair_dados_medium(tag):
    """Obtém artigos do Medium via feed RSS, trata e retorna um DataFrame."""
    url = f"https://medium.com/feed/tag/{tag}"
    print(f"Coletando dados do feed: {url}")

    try:
        feed = feedparser.parse(url)
        if not feed.entries:
            print(f"Aviso: Nenhum artigo encontrado para a tag '{tag}'.")
            return pd.DataFrame()

        lista_artigos = []
        for entry in feed.entries:
            artigo = {
                "titulo": entry.get("title", ""),
                "autor": entry.get("author", "Anônimo"),
                "link": entry.get("link", ""),
                "data_publicacao": datetime(*entry.published_parsed[:6]) if entry.get("published_parsed") else None,
                "tag_buscada": tag,
                "coletado_em": datetime.now()
            }
            lista_artigos.append(artigo)

        df = pd.DataFrame(lista_artigos)

        # Garante a tipagem correta antes do envio (Schema Enforcement)
        if not df.empty:
            df["data_publicacao"] = pd.to_datetime(df["data_publicacao"])
            df["coletado_em"] = pd.to_datetime(df["coletado_em"])

        return df

    except Exception as e:
        print(f"Erro crítico na extração dos dados: {e}")
        return pd.DataFrame()
