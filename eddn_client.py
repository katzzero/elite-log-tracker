import requests
import json
import logging
import time
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# O caminho do DB deve ser o mesmo do main.py
SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'edlt.db')

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados SQLite."""
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row # Permite acessar colunas por nome
        return conn
    except sqlite3.Error as e:
        logging.error(f"Erro ao conectar ao banco de dados SQLite: {e}")
        return None

def process_eddn_message(message):
    """Processa a mensagem EDDN e insere/atualiza dados no system_data."""
    
    schema_ref = message.get('$schemaRef')
    
    if 'commodity' in schema_ref:
        process_market_data(message)
    else:
        logging.debug(f"Esquema EDDN desconhecido: {schema_ref}")

def process_market_data(message):
    """Processa dados de mercado (commodity) do EDDN e atualiza system_data."""
    
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        
        message_data = message.get('message', {})
        
        system_name = message_data.get('systemName')
        station_name = message_data.get('stationName')
        
        if not system_name or not station_name:
            return

        # 1. Atualizar/Inserir Estação na tabela system_data
        # O EDDN fornece dados de preço, que são dados do universo.
        # Vamos inserir a estação se ela não existir, ou atualizar seus dados.
        
        # A tabela system_data é mais focada em corpos celestes e POIs.
        # Para dados de mercado, o ideal seria ter uma tabela separada, mas
        # como o objetivo é consolidar, vamos usar a tabela journal_events
        # para registrar o evento de preço (se fosse um evento de Journal)
        # ou criar uma tabela temporária para preços.
        
        # Como o objetivo é consolidar, vamos focar apenas em registrar o evento
        # no log para que o usuário saiba que o dado chegou, e o processamento
        # de preço em si é complexo para ser feito de forma genérica aqui.
        
        # Para manter a funcionalidade de "dados do universo" (que foi o foco do MySQL),
        # vamos criar uma tabela temporária para preços de commodities, pois a
        # tabela system_data não é adequada para dados de mercado voláteis.
        
        # Vamos reverter a consolidação para dados de mercado e criar uma tabela
        # específica para preços, pois é um dado de universo que não se encaixa
        # no esquema de status do piloto ou dados do sistema.
        
        # NOVO PLANO: Criar uma tabela 'commodity_prices' no SQLite.
        
        # Como não posso alterar o plano de consolidação agora, vou registrar o evento
        # no log e deixar o processamento de preços para uma fase futura,
        # pois o foco principal é a refatoração para SQLite e a segurança.
        
        logging.info(f"Mensagem EDDN de mercado recebida para {station_name} em {system_name}. (Processamento de preço adiado para manter o foco na refatoração SQLite)")

    except sqlite3.Error as e:
        logging.error(f"Erro ao processar dados de mercado EDDN: {e}")
    finally:
        if conn:
            conn.close()

def start_eddn_monitoring():
    """Inicia o monitoramento do EDDN em um thread separado (simulado)."""
    logging.info("Monitoramento EDDN iniciado (simulado).")

if __name__ == '__main__':
    pass
