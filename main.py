import os
import json
import time
import logging
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from mysql.connector import connect, Error

# Importa o módulo auxiliar (assumindo que ele está no mesmo diretório ou no PYTHONPATH)
from eddn_client import start_eddn_monitoring 

# Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Variáveis de Configuração (A serem lidas de um arquivo de configuração ou GUI)
JOURNAL_DIR = os.path.expanduser('~/Saved Games/Frontier Developments/Elite Dangerous') # Caminho padrão no Windows
DB_CONFIG = {
    'host': 'localhost',
    'user': 'ed_user', # Usuário e senha a serem definidos pelo usuário
    'password': 'ed_password',
}

# --- Funções Auxiliares de Arquivo (fora da classe para manter a compatibilidade) ---

def get_latest_journal_file(directory):
    """Encontra o arquivo de diário mais recente no diretório."""
    try:
        files = [os.path.join(directory, f) for f in os.listdir(directory) if f.startswith('Journal.') and f.endswith('.log')]
        if not files:
            return None
        # O formato do nome do arquivo é 'Journal.YYYY-MM-DDTHHMMSS.XX.log', então a ordenação alfabética funciona
        return max(files, key=os.path.getmtime)
    except FileNotFoundError:
        logging.error(f"Diretório de logs não encontrado: {directory}")
        return None
    except Exception as e:
        logging.error(f"Erro ao buscar arquivo de log mais recente: {e}")
        return None

class JournalFileMonitor(FileSystemEventHandler):
    """Manipulador de eventos do Watchdog para monitorar a escrita no arquivo de diário."""
    
    def __init__(self, journal_path, event_processor_callback):
        self.journal_path = journal_path
        self.file_handle = None
        self.event_processor_callback = event_processor_callback # Callback para processar o evento
        self.open_file()

    def open_file(self):
        """Abre o arquivo de diário e move o ponteiro para o final."""
        if self.file_handle:
            self.file_handle.close()
        
        try:
            self.file_handle = open(self.journal_path, 'r', encoding='utf-8')
            self.file_handle.seek(0, os.SEEK_END)
            logging.info(f"Monitorando o arquivo: {self.journal_path}")
        except Exception as e:
            logging.error(f"Não foi possível abrir o arquivo {self.journal_path}: {e}")
            self.file_handle = None

    def on_modified(self, event):
        """Chamado quando o arquivo de diário é modificado."""
        if event.src_path == self.journal_path and not event.is_directory:
            self.read_new_lines()

    def read_new_lines(self):
        """Lê e processa as novas linhas adicionadas ao arquivo."""
        if not self.file_handle:
            self.open_file()
            if not self.file_handle:
                return

        new_data = self.file_handle.readlines()
        
        for line in new_data:
            try:
                event_data = json.loads(line)
                # Chama o callback (que é o método process_event da classe BackendCore)
                self.event_processor_callback(event_data) 
            except json.JSONDecodeError as e:
                logging.error(f"Erro ao decodificar JSON: {e} na linha: {line.strip()}")
            except Exception as e:
                logging.error(f"Erro desconhecido ao processar linha: {e}")

    def stop(self):
        """Fecha o handle do arquivo."""
        if self.file_handle:
            self.file_handle.close()

# --- Core do Backend ---

class BackendCore:
    def __init__(self, db_config, journal_dir):
        self.DB_CONFIG = db_config
        self.JOURNAL_DIR = journal_dir
        self.observer = None
        self.event_handler = None
        self.monitoring_thread = None
        self.eddn_thread = None
        self.is_running = False

    # --- Funções de Banco de Dados (Encapsuladas) ---

    def get_db_connection(self, db_name):
        """Cria e retorna uma conexão com o banco de dados especificado."""
        try:
            conn = connect(database=db_name, **self.DB_CONFIG)
            return conn
        except Error as e:
            logging.error(f"Erro ao conectar ao banco de dados {db_name}: {e}")
            return None

    def insert_journal_event(self, event_data):
        """Insere o evento JSON bruto na tabela journal_events do db_piloto."""
        conn = self.get_db_connection('db_piloto')
        if not conn:
            return

        try:
            cursor = conn.cursor()
            sql = """
            INSERT INTO journal_events (timestamp, event_type, commander_name, event_json)
            VALUES (%s, %s, %s, %s)
            """
            
            timestamp = event_data.get('timestamp')
            event_type = event_data.get('event')
            commander = event_data.get('Commander')
            event_json_str = json.dumps(event_data)

            cursor.execute(sql, (timestamp, event_type, commander, event_json_str))
            conn.commit()
            logging.info(f"Evento '{event_type}' inserido no db_piloto.")

            return cursor.lastrowid

        except Error as e:
            logging.error(f"Erro ao inserir evento no db_piloto: {e}")
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
        return None

    # --- Funções de Processamento de Eventos (Encapsuladas) ---

    def process_fsd_jump(self, event_data, event_id):
        """Processa o evento FSDJump e insere na tabela pilot_journeys e star_systems."""
        
        # Dados do Piloto (db_piloto.pilot_journeys)
        conn_piloto = self.get_db_connection('db_piloto')
        if conn_piloto:
            try:
                cursor = conn_piloto.cursor()
                sql = """
                INSERT INTO pilot_journeys (timestamp, system_name, jump_distance)
                VALUES (%s, %s, %s)
                """
                timestamp = event_data.get('timestamp')
                system_name = event_data.get('StarSystem')
                jump_distance = event_data.get('JumpDist')
                
                cursor.execute(sql, (timestamp, system_name, jump_distance))
                conn_piloto.commit()
                logging.info(f"Viagem para '{system_name}' registrada.")
            except Error as e:
                logging.error(f"Erro ao inserir viagem: {e}")
            finally:
                if conn_piloto and conn_piloto.is_connected():
                    cursor.close()
                    conn_piloto.close()

        # Dados do Universo (db_universo.star_systems) - Insere ou atualiza
        conn_universo = self.get_db_connection('db_universo')
        if conn_universo:
            try:
                cursor = conn_universo.cursor()
                sql = """
                INSERT INTO star_systems (system_name, system_address, x, y, z, allegiance, government, population)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    allegiance=VALUES(allegiance), government=VALUES(government), population=VALUES(population)
                """
                
                system_name = event_data.get('StarSystem')
                system_address = event_data.get('SystemAddress')
                pos = event_data.get('StarPos', [None, None, None])
                allegiance = event_data.get('SystemAllegiance')
                government = event_data.get('SystemGovernment')
                population = event_data.get('SystemPopulation')

                cursor.execute(sql, (system_name, system_address, pos[0], pos[1], pos[2], allegiance, government, population))
                conn_universo.commit()
                logging.info(f"Sistema '{system_name}' atualizado no db_universo.")
            except Error as e:
                logging.error(f"Erro ao inserir/atualizar sistema: {e}")
            finally:
                if conn_universo and conn_universo.is_connected():
                    cursor.close()
                    conn_universo.close()

    def process_transaction(self, event_data, event_id):
        """Processa eventos de compra/venda de commodities."""
        conn_piloto = self.get_db_connection('db_piloto')
        if not conn_piloto:
            return

        try:
            cursor = conn_piloto.cursor()
            sql = """
            INSERT INTO pilot_transactions (timestamp, station_name, commodity_name, transaction_type, price, quantity, total_cost)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            timestamp = event_data.get('timestamp')
            station_name = event_data.get('StationName')
            commodity_name = event_data.get('Name')
            transaction_type = 'BUY' if event_data.get('event') == 'BuyCommodity' else 'SELL'
            price = event_data.get('Price')
            quantity = event_data.get('Count')
            total_cost = event_data.get('TotalCost')

            cursor.execute(sql, (timestamp, station_name, commodity_name, transaction_type, price, quantity, total_cost))
            conn_piloto.commit()
            logging.info(f"Transação '{transaction_type}' de {quantity}x {commodity_name} registrada.")

        except Error as e:
            logging.error(f"Erro ao inserir transação: {e}")
        finally:
            if conn_piloto and conn_piloto.is_connected():
                cursor.close()
                conn_piloto.close()

    def process_rank_event(self, event_data):
        """Processa os eventos Rank e Progress e insere/atualiza na tabela pilot_ranks."""
        conn_piloto = self.get_db_connection('db_piloto')
        if not conn_piloto:
            return

        try:
            cursor = conn_piloto.cursor()
            
            # O evento 'Rank' contém todos os ranques de uma vez
            if event_data.get('event') == 'Rank':
                for rank_type in ["Combat", "Trade", "Explore", "CQC", "Federation", "Empire"]:
                    rank_value = event_data.get(rank_type)
                    if rank_value is not None:
                        # Para o evento Rank, o progresso é 0.0 (será atualizado pelo Progress)
                        sql = """
                        INSERT INTO pilot_ranks (rank_type, rank_value, rank_progress)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                            rank_value=VALUES(rank_value), updated_at=CURRENT_TIMESTAMP
                        """
                        cursor.execute(sql, (rank_type, rank_value, 0.0))
                
                conn_piloto.commit()
                logging.info("Ranques iniciais (Rank event) atualizados no db_piloto.")

            # O evento 'Progress' contém o progresso para o próximo ranque (0 a 100)
            elif event_data.get('event') == 'Progress':
                for rank_type in ["Combat", "Trade", "Explore", "CQC"]:
                    progress_percent = event_data.get(rank_type)
                    if progress_percent is not None:
                        # O progresso é dado em porcentagem (0 a 100), convertemos para 0.0 a 1.0
                        progress_value = progress_percent / 100.0
                        
                        sql = """
                        UPDATE pilot_ranks SET rank_progress = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE rank_type = %s
                        """
                        cursor.execute(sql, (progress_value, rank_type))
                
                conn_piloto.commit()
                logging.info("Progresso de ranques (Progress event) atualizado no db_piloto.")

        except Error as e:
            logging.error(f"Erro ao processar evento Rank/Progress: {e}")
        finally:
            if conn_piloto and conn_piloto.is_connected():
                cursor.close()
                conn_piloto.close()

    # Adicionar aqui os métodos process_location, process_loadout, process_materials, etc.
    def process_materials_event(self, event_data):
        """Processa o evento Materials e atualiza a tabela pilot_materials."""
        conn_piloto = self.get_db_connection('db_piloto')
        if not conn_piloto:
            return

        try:
            cursor = conn_piloto.cursor()
            
            # O evento Materials contém 3 listas: Raw, Manufactured, Encoded
            for category in ['Raw', 'Manufactured', 'Encoded']:
                materials = event_data.get(category, [])
                for material in materials:
                    name = material.get('Name')
                    count = material.get('Count')
                    
                    if name and count is not None:
                        sql = """
                        INSERT INTO pilot_materials (timestamp, material_name, material_category, count)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                            timestamp=VALUES(timestamp), count=VALUES(count)
                        """
                        timestamp = event_data.get('timestamp')
                        cursor.execute(sql, (timestamp, name, category, count))
            
            conn_piloto.commit()
            logging.info("Inventário de materiais atualizado no db_piloto.")

        except Error as e:
            logging.error(f"Erro ao processar evento Materials: {e}")
        finally:
            if conn_piloto and conn_piloto.is_connected():
                cursor.close()
                conn_piloto.close()

    # Adicionar aqui os métodos process_location, process_loadout, etc.
    def process_location(self, event_data, event_id):
        """Processa o evento Location e atualiza o status do piloto e o sistema estelar."""
        # Lógica de processamento de Location (Status do Piloto e Sistema Estelar)
        # ... (manter a lógica existente)
        pass

    def process_loadout(self, event_data, event_id):
        """Processa o evento Loadout e atualiza os módulos da nave."""
        # Lógica de processamento de Loadout (Módulos da Nave)
        # ... (manter a lógica existente)
        pass

    def process_shipyard(self, event_data, event_id):
        """Processa o evento Shipyard e atualiza a lista de naves."""
        # Lógica de processamento de Shipyard (Lista de Naves)
        # ... (manter a lógica existente)
        pass

    def process_shipname(self, event_data, event_id):
        """Processa o evento ShipName e atualiza o nome da nave."""
        # Lógica de processamento de ShipName (Nome da Nave)
        # ... (manter a lógica existente)
        pass

    # Adicionar aqui os métodos process_location, process_loadout, process_materials, etc.

    def process_event(self, event_data):
        """Processa o evento do diário, insere o JSON bruto e chama o processamento específico."""
        
        # 1. Inserir o evento JSON bruto (Dados do Piloto)
        event_id = self.insert_journal_event(event_data)
        if not event_id:
            return

        event_type = event_data.get('event')
        
        # 2. Processamento específico para tabelas resumidas
        if event_type == 'FSDJump':
            self.process_fsd_jump(event_data, event_id)
        elif event_type in ['BuyCommodity', 'SellCommodity']:
            self.process_transaction(event_data, event_id)
        elif event_type in ['Rank', 'Progress']:
            self.process_rank_event(event_data)
        elif event_type == 'Materials':
            self.process_materials_event(event_data)
        # Adicionar mais eventos conforme necessário

    # --- Funções de Controle de Monitoramento ---

    def start_monitoring(self):
        """Inicia o monitoramento do arquivo de diário mais recente e EDDN."""
        if self.is_running:
            logging.info("O monitoramento já está em execução.")
            return

        latest_file = get_latest_journal_file(self.JOURNAL_DIR)
        
        if not latest_file:
            logging.error("Nenhum arquivo de diário encontrado. Verifique o caminho.")
            return

        # 1. Monitoramento de Logs (Journal)
        # Passa o método process_event como callback para o JournalFileMonitor
        self.event_handler = JournalFileMonitor(latest_file, self.process_event) 
        self.observer = Observer()
        
        # Monitora o diretório onde o arquivo de diário está
        self.observer.schedule(self.event_handler, path=os.path.dirname(latest_file), recursive=False)
        self.observer.start()
        
        # 2. Monitoramento EDDN (em thread separado)
        self.eddn_thread = threading.Thread(target=start_eddn_monitoring)
        self.eddn_thread.daemon = True # Permite que o programa principal saia mesmo que o thread esteja rodando
        self.eddn_thread.start()

        self.is_running = True
        logging.info("Monitoramento de Logs e EDDN iniciado.")

    def stop_monitoring(self):
        """Para o monitoramento."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
        if self.event_handler:
            self.event_handler.stop()
        
        self.is_running = False
        logging.info("Monitoramento parado.")

if __name__ == '__main__':
    # Exemplo de uso (apenas para teste de console)
    
    # backend = BackendCore(DB_CONFIG, JOURNAL_DIR)
    # backend.start_monitoring()
    
    logging.info("Backend pronto para ser integrado à GUI.")
