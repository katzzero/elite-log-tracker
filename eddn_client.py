import os  # FIX: Import faltando
import requests
import json
import logging
import time
import sqlite3
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# O caminho do DB deve ser o mesmo do main.py
SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'edlt.db')

def get_db_connection() -> Optional[sqlite3.Connection]:
    """Cria e retorna uma conexão com o banco de dados SQLite."""
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
        return conn
    except sqlite3.Error as e:
        logging.error(f"Erro ao conectar ao banco de dados SQLite: {e}")
        return None

def process_eddn_message(message: Dict[str, Any]) -> None:
    """Processa a mensagem EDDN e insere/atualiza dados no system_data."""
    
    schema_ref = message.get('$schemaRef', '')
    
    if 'commodity' in schema_ref:
        process_market_data(message)
    else:
        logging.debug(f"Esquema EDDN desconhecido: {schema_ref}")

def process_market_data(message: Dict[str, Any]) -> None:
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

        # NOTA: Processamento de preços de commodities foi adiado
        # para manter o foco na refatoração SQLite e segurança.
        # Esta funcionalidade requer uma tabela dedicada 'commodity_prices'
        # que não faz parte do escopo atual.
        
        logging.info(f"Mensagem EDDN de mercado recebida para {station_name} em {system_name}. "
                    f"(Processamento de preço adiado para manter o foco na refatoração SQLite)")

    except sqlite3.Error as e:
        logging.error(f"Erro ao processar dados de mercado EDDN: {e}")
    finally:
        if conn:
            conn.close()

def start_eddn_monitoring() -> None:
    """Inicia o monitoramento do EDDN em um thread separado (simulado)."""
    logging.info("Monitoramento EDDN iniciado (simulado).")
    # TODO: Implementar cliente EDDN real usando websockets
    # import websocket
    # ws = websocket.WebSocketApp("wss://eddn.edcd.io:4430/upload/",
    #                            on_message=on_message,
    #                            on_error=on_error,
    #                            on_close=on_close)
    # ws.run_forever()

if __name__ == '__main__':
    pass
