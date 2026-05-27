

# Medium Tech Analytics Pipeline

Este é um projeto de Engenharia de Dados que implementa um pipeline **ETL (Extract, Transform, Load)** dinâmico. O objetivo é minerar artigos recentes do Medium através de Feeds RSS, realizar a transformação e tipagem dos dados usando Python e Pandas, e armazená-los de forma incremental em um Data Warehouse na nuvem com o Google Cloud BigQuery. Por fim, os dados são integrados ao Google Looker Studio para visualização de indicadores.

---

## Arquitetura do Projeto

O fluxo de dados segue a arquitetura moderna de plataformas de dados:

1. **Extração (Extract):** Coleta automatizada do XML do Feed RSS do Medium usando a biblioteca `feedparser`.
2. **Transformação (Transform):** Tratamento de strings, tratamento de exceções para campos ausentes e conversão de timestamps para tipos nativos do Pandas (`datetime64[ns]`), garantindo a compatibilidade PyArrow.
3. **Carga (Load):** Ingestão de dados no Google Cloud BigQuery no modo append (`WRITE_APPEND`), preservando o histórico.
4. **Visualização (BI):** Construção de dashboards interativos no Looker Studio conectados diretamente ao BigQuery.

---

##  Tecnologias e Ferramentas

* **Linguagem:** Python 3.x
* **Manipulação de Dados:** Pandas
* **Engine de Transição:** PyArrow / Pandas-GBQ
* **Data Warehouse:** Google Cloud BigQuery
* **Camada de BI:** Google Looker Studio
* **Segurança:** Python-dotenv (Variáveis de ambiente)

---
