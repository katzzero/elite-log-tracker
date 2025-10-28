import requests
import json
import logging
import time
from mysql.connector import connect, Error

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuração de Banco de Dados (deve ser a mesma do main.py)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'ed_user',
    'password': 'ed_password',
}

def get_db_connection(db_name):
    """Cria e retorna uma conexão com o banco de dados especificado."""
    try:
        conn = connect(database=db_name, **DB_CONFIG)
        return conn
    except Error as e:
        logging.error(f"Erro ao conectar ao banco de dados {db_name}: {e}")
        return None

def process_eddn_message(message):
    """Processa a mensagem EDDN e insere/atualiza dados no db_universo."""
    
    # A mensagem EDDN é um JSON que contém um cabeçalho e um esquema de dados
    schema_ref = message.get('$schemaRef')
    
    if 'commodity' in schema_ref:
        process_market_data(message)
    elif 'station' in schema_ref:
        # Outros esquemas (ex: Journal events, mas vamos focar no Market por enquanto)
        logging.info(f"Mensagem EDDN de {schema_ref} recebida, mas não processada.")
        pass
    else:
        logging.debug(f"Esquema EDDN desconhecido: {schema_ref}")

def process_market_data(message):
    """Processa dados de mercado (commodity) do EDDN."""
    
    conn_universo = get_db_connection('db_universo')
    if not conn_universo:
        return

    try:
        cursor = conn_universo.cursor()
        
        header = message.get('header', {})
        message_data = message.get('message', {})
        
        # 1. Atualizar/Inserir Sistema Estelar
        system_name = message_data.get('systemName')
        if system_name:
            # O EDDN não fornece coordenadas, mas fornece o nome do sistema
            sql_system = """
            INSERT INTO star_systems (system_name)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE updated_at=NOW()
            """
            cursor.execute(sql_system, (system_name,))
            conn_universo.commit()
        
        # 2. Atualizar/Inserir Estação
        station_name = message_data.get('stationName')
        market_id = message_data.get('marketId')
        if station_name and system_name:
            sql_station = """
            INSERT INTO stations (station_name, system_name, market_id)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE updated_at=NOW(), market_id=VALUES(market_id)
            """
            cursor.execute(sql_station, (station_name, system_name, market_id))
            conn_universo.commit()

        # 3. Inserir Preços de Commodities
        timestamp = message_data.get('timestamp')
        
        for commodity in message_data.get('commodities', []):
            sql_price = """
            INSERT INTO commodity_prices (timestamp, station_name, commodity_name, supply, demand, buy_price, sell_price)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            commodity_name = commodity.get('name')
            supply = commodity.get('supply')
            demand = commodity.get('demand')
            buy_price = commodity.get('buyPrice')
            sell_price = commodity.get('sellPrice')
            
            cursor.execute(sql_price, (timestamp, station_name, commodity_name, supply, demand, buy_price, sell_price))
        
        conn_universo.commit()
        logging.info(f"Dados de mercado de {len(message_data.get('commodities', []))} commodities inseridos para {station_name} em {system_name}.")

    except Error as e:
        logging.error(f"Erro ao processar dados de mercado EDDN: {e}")
    finally:
        if conn_universo and conn_universo.is_connected():
            cursor.close()
            conn_universo.close()

def fetch_eddn_stream(callback):
    """Conecta-se ao stream de dados EDDN e chama o callback para cada mensagem."""
    # O EDDN usa um stream de dados comprimidos em Zlib via ZeroMQ.
    # Para simplificar e evitar dependências complexas (ZeroMQ, Zlib),
    # vamos simular a busca de dados de uma API que fornece dados agregados,
    # ou usar um endpoint de teste/amostra se disponível.
    
    # Para uma implementação real, seria necessário:
    # 1. Instalar e configurar ZeroMQ (pyzmq)
    # 2. Conectar-se ao endpoint ZeroMQ (tcp://eddn.edcd.io:9500)
    # 3. Descomprimir e decodificar a mensagem
    
    # SIMULAÇÃO: Como não podemos instalar ZeroMQ, vamos buscar dados agregados
    # de uma fonte alternativa que utilize dados EDDN, como o EDDB (se tivesse API),
    # ou simplesmente informar o usuário sobre a necessidade de ZeroMQ.
    
    # Alternativa: Usar um endpoint de teste ou um agregador público que use HTTP.
    # Não há um endpoint HTTP de stream fácil de usar.
    
    logging.warning("Para o monitoramento em tempo real do EDDN, é necessário o ZeroMQ (pyzmq) e descompressão Zlib, o que torna a implementação complexa no ambiente atual.")
    logging.warning("O código abaixo é um placeholder. A integração real com o EDDN requer bibliotecas adicionais.")

    # Exemplo de como a função de processamento seria chamada se tivéssemos o stream:
    # while True:
    #     try:
    #         # ... código para receber e descompactar a mensagem ...
    #         message = json.loads(decompressed_data)
    #         callback(message)
    #     except Exception as e:
    #         logging.error(f"Erro no stream EDDN: {e}")
    #         time.sleep(5)

# Função para ser chamada no loop de eventos da GUI
def start_eddn_monitoring():
    """Inicia o monitoramento do EDDN em um thread separado (idealmente)."""
    # fetch_eddn_stream(process_eddn_message)
    logging.info("Monitoramento EDDN iniciado (simulado).")

if __name__ == '__main__':
    # Teste de simulação (requer MySQL configurado)
    # start_eddn_monitoring()
    pass

