import os
import json
import time
import logging
import threading
import sqlite3
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Importa o módulo auxiliar (assumindo que ele está no mesmo diretório ou no PYTHONPATH)
from eddn_client import start_eddn_monitoring 
from backend.rank_data import RANK_NAMES, PILOTS__FEDERATION_RANKS, SUPERPOWER_RANKS
from backend.material_limits import MATERIAL_LIMITS

# Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Variáveis de Configuração
JOURNAL_DIR = os.path.expanduser('~/Saved Games/Frontier Developments/Elite Dangerous') # Caminho padrão no Windows
SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'edlt.db')

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
    def __init__(self, journal_dir):
        self.JOURNAL_DIR = journal_dir
        self.observer = None
        self.event_handler = None
        self.monitoring_thread = None
        self.eddn_thread = None
        self.is_running = False
        self.db_path = SQLITE_DB_PATH
        self.initialize_db()

    # --- Funções de Banco de Dados (SQLite) ---

    def get_db_connection(self):
        """Cria e retorna uma conexão com o banco de dados SQLite."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row # Permite acessar colunas por nome
            return conn
        except sqlite3.Error as e:
            logging.error(f"Erro ao conectar ao banco de dados SQLite: {e}")
            return None

    def initialize_db(self):
        """Cria as tabelas se não existirem."""
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            with open(os.path.join(os.path.dirname(__file__), 'sqlite_schema.sql'), 'r') as f:
                sql_script = f.read()
            conn.executescript(sql_script)
            conn.commit()
            logging.info("Banco de dados SQLite inicializado com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao inicializar o banco de dados SQLite: {e}")
        finally:
            if conn:
                conn.close()

    def insert_journal_event(self, event_data):
        """Insere o evento JSON bruto na tabela journal_events e retorna o ID."""
        conn = self.get_db_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            
            timestamp = event_data.get('timestamp')
            event_type = event_data.get('event')
            event_json_str = json.dumps(event_data)
            
            # Cria um hash para garantir a unicidade (timestamp + event_type + 10 primeiros chars do JSON)
            # Isso é uma heurística para evitar duplicatas sem processar o arquivo inteiro
            unique_str = f"{timestamp}{event_type}{event_json_str[:10]}"
            event_hash = hashlib.sha256(unique_str.encode('utf-8')).hexdigest()

            sql = """
            INSERT OR IGNORE INTO journal_events (timestamp, event_type, event_data, event_hash)
            VALUES (?, ?, ?, ?)
            """
            
            cursor.execute(sql, (timestamp, event_type, event_json_str, event_hash))
            conn.commit()
            
            if cursor.rowcount > 0:
                logging.info(f"Evento '{event_type}' inserido no SQLite.")
                return cursor.lastrowid
            else:
                # O evento foi ignorado (duplicado)
                return None

        except sqlite3.Error as e:
            logging.error(f"Erro ao inserir evento no SQLite: {e}")
        finally:
            if conn:
                conn.close()
        return None

    # --- Funções de Processamento de Eventos (SQLite) ---

    def update_pilot_status(self, event_data):
        """Atualiza o status do piloto (ranques, localização, etc.) na tabela pilot_status."""
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            
            # 1. Obter o nome do piloto (assumindo que o evento 'LoadGame' ou 'Commander' já ocorreu)
            # Para simplificar, vamos usar um nome padrão se não for encontrado, mas o ideal é buscar o último CommanderName
            pilot_name = event_data.get('Commander', 'CMDR_Unknown')
            
            # 2. Inserir ou atualizar o registro do piloto
            cursor.execute("INSERT OR IGNORE INTO pilot_status (pilot_name, last_update) VALUES (?, ?)", 
                           (pilot_name, event_data.get('timestamp')))
            
            # 3. Construir a query de atualização
            update_fields = {}
            params = []
            
            # Ranques (do evento 'Rank')
            if event_data.get('event') == 'Rank':
                for rank_type in ['Combat', 'Trade', 'Explore', 'CQC', 'Federation', 'Empire']:
                    if rank_type in event_data:
                        update_fields[f'rank_{rank_type.lower()}'] = event_data[rank_type]
            
            # Progresso (do evento 'Progress')
            elif event_data.get('event') == 'Progress':
                for rank_type in ['Combat', 'Trade', 'Explore', 'CQC', 'Federation', 'Empire']:
                    if rank_type in event_data:
                        update_fields[f'progress_{rank_type.lower()}'] = event_data[rank_type] / 100.0 # Converte para 0.0 a 1.0
            
            # Localização (do evento 'Location' ou 'FSDJump')
            elif event_data.get('event') in ['Location', 'FSDJump']:
                update_fields['system_name'] = event_data.get('StarSystem')
                update_fields['station_name'] = event_data.get('StationName')
                
            # Ship (do evento 'Loadout' ou 'ShipyardSwap')
            elif event_data.get('event') in ['Loadout', 'ShipyardSwap']:
                update_fields['ship_id'] = event_data.get('ShipID')
                update_fields['ship_name'] = event_data.get('ShipName')
                update_fields['ship_model'] = event_data.get('Ship')
            
            # 4. Executar a atualização
            if update_fields:
                update_fields['last_update'] = event_data.get('timestamp')
                
                set_clause = ", ".join([f"{k} = ?" for k in update_fields.keys()])
                params = list(update_fields.values())
                params.append(pilot_name)
                
                sql = f"UPDATE pilot_status SET {set_clause} WHERE pilot_name = ?"
                cursor.execute(sql, params)
                conn.commit()
                logging.info(f"Status do piloto atualizado por evento '{event_data.get('event')}'.")

        except sqlite3.Error as e:
            logging.error(f"Erro ao atualizar status do piloto: {e}")
        finally:
            if conn:
                conn.close()

    def update_pilot_materials(self, event_data):
        """Atualiza o inventário de materiais na tabela pilot_materials."""
        if event_data.get('event') != 'Materials':
            return
            
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            
            # Limpa a tabela antes de inserir o novo inventário completo
            cursor.execute("DELETE FROM pilot_materials")
            
            materials = event_data.get('Raw', []) + event_data.get('Manufactured', []) + event_data.get('Encoded', [])
            
            for material in materials:
                name = material.get('Name')
                count = material.get('Count')
                category = material.get('Category')
                
                sql = "INSERT INTO pilot_materials (material_name, category, count) VALUES (?, ?, ?)"
                cursor.execute(sql, (name, category, count))
                
            conn.commit()
            logging.info(f"Inventário de materiais atualizado com {len(materials)} itens.")

        except sqlite3.Error as e:
            logging.error(f"Erro ao atualizar inventário de materiais: {e}")
        finally:
            if conn:
                conn.close()

    def insert_pilot_profit(self, event_data, profit_type, amount):
        """Insere um registro de lucro na tabela pilot_profit."""
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            sql = "INSERT INTO pilot_profit (timestamp, profit_type, amount) VALUES (?, ?, ?)"
            cursor.execute(sql, (event_data.get('timestamp'), profit_type, amount))
            conn.commit()
            logging.info(f"Lucro de {profit_type} de {amount} Cr registrado.")

        except sqlite3.Error as e:
            logging.error(f"Erro ao inserir lucro: {e}")
        finally:
            if conn:
                conn.close()

    def update_system_data(self, event_data):
        """Atualiza dados do sistema (corpos celestes, estações, sinais) na tabela system_data."""
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            event_type = event_data.get('event')
            system_name = event_data.get('StarSystem')
            
            if not system_name:
                return

            # Limpa dados antigos do sistema ao entrar em um novo sistema
            if event_type == 'FSDJump':
                cursor.execute("DELETE FROM system_data WHERE system_name != ?", (system_name,))
                conn.commit()
                logging.info(f"Dados de sistemas antigos limpos ao entrar em {system_name}.")
                
            # Processa corpos celestes (do evento 'FSDJump' ou 'Location' - SystemData)
            if event_type in ['FSDJump', 'Location'] and 'Body' in event_data:
                # O evento FSDJump/Location contém dados da estrela principal e da estação
                
                # 1. Estrela Principal
                star_name = event_data.get('Body')
                star_type = event_data.get('StarType')
                star_data = json.dumps(event_data)
                
                sql = "INSERT OR REPLACE INTO system_data (name, system_name, type, distance_ls, data_json) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(sql, (star_name, system_name, 'STAR', 0.0, star_data))
                
                # 2. Estação (se estiver atracado)
                if event_data.get('StationName'):
                    station_name = event_data.get('StationName')
                    station_type = event_data.get('StationType')
                    
                    # Distância da estrela principal não está no Location/FSDJump, mas a inserimos
                    cursor.execute(sql, (station_name, system_name, 'STATION', None, json.dumps(event_data)))
                    
            # Processa escaneamento de corpos (do evento 'Scan')
            elif event_type == 'Scan':
                body_name = event_data.get('BodyName')
                body_type = event_data.get('BodyType')
                distance = event_data.get('DistanceFromArrivalLS')
                
                sql = "INSERT OR REPLACE INTO system_data (name, system_name, type, distance_ls, data_json) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(sql, (body_name, system_name, body_type, distance, json.dumps(event_data)))
                
            # Processa sinais (do evento 'FSSSignalDiscovered')
            elif event_type == 'FSSSignalDiscovered':
                signal_name = event_data.get('SignalName')
                signal_type = event_data.get('SignalType')
                
                sql = "INSERT OR REPLACE INTO system_data (name, system_name, type, distance_ls, data_json) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(sql, (signal_name, system_name, 'SIGNAL', None, json.dumps(event_data)))
                
            conn.commit()
            logging.info(f"Dados do sistema '{system_name}' atualizados por evento '{event_type}'.")

        except sqlite3.Error as e:
            logging.error(f"Erro ao atualizar dados do sistema: {e}")
        finally:
            if conn:
                conn.close()

    def update_ship_modules(self, event_data):
        """Atualiza o loadout da nave na tabela ship_modules."""
        if event_data.get('event') != 'Loadout':
            return
            
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            ship_id = event_data.get('ShipID')
            
            # Limpa o loadout antigo para esta nave
            cursor.execute("DELETE FROM ship_modules WHERE ship_id = ?", (ship_id,))
            
            modules = event_data.get('Modules', [])
            
            for module in modules:
                slot = module.get('Slot')
                item = module.get('Item')
                health = module.get('Health', 1.0) # Assume 1.0 se não houver saúde
                
                sql = "INSERT INTO ship_modules (ship_id, slot, module, health) VALUES (?, ?, ?, ?)"
                cursor.execute(sql, (ship_id, slot, item, health))
                
            conn.commit()
            logging.info(f"Loadout da nave {ship_id} atualizado com {len(modules)} módulos.")

        except sqlite3.Error as e:
            logging.error(f"Erro ao atualizar módulos da nave: {e}")
        finally:
            if conn:
                conn.close()

    def process_event(self, event_data):
        """Processa um evento do diário e o insere no banco de dados."""
        
        # 1. Insere o evento bruto e verifica se é duplicado
        event_id = self.insert_journal_event(event_data)
        if event_id is None:
            return # Evento duplicado ou erro de inserção

        event_type = event_data.get('event')

        # 2. Atualiza o status do piloto (ranques, localização, nave)
        self.update_pilot_status(event_data)
        
        # 3. Processa eventos de lucro
        if event_type == 'MarketSell':
            self.insert_pilot_profit(event_data, 'TRADE', event_data.get('SellPrice') * event_data.get('Count'))
        elif event_type == 'Bounty':
            self.insert_pilot_profit(event_data, 'BOUNTY', event_data.get('Reward'))
        elif event_type == 'MultiSellExplorationData':
            self.insert_pilot_profit(event_data, 'EXPLORATION', event_data.get('TotalEarnings'))
        elif event_type == 'Scan' and event_data.get('ScanType') == 'Detailed':
            # Lucro de Cartografia (Exploração) - O valor exato é complexo, mas o evento Scan é o gatilho
            # Para simplificar, vamos registrar o evento, o valor será somado no SellExplorationData
            pass
        elif event_type == 'SellOrganicData':
            self.insert_pilot_profit(event_data, 'EXOBIOLOGY', event_data.get('TotalEarnings'))
            
        # 4. Atualiza o inventário de materiais
        if event_type == 'Materials':
            self.update_pilot_materials(event_data)
            
        # 5. Atualiza dados do sistema (corpos, estações, sinais)
        if event_type in ['FSDJump', 'Location', 'Scan', 'FSSSignalDiscovered']:
            self.update_system_data(event_data)
            
        # 6. Atualiza módulos da nave
        if event_type == 'Loadout':
            self.update_ship_modules(event_data)

    # --- Funções de Controle ---

    def start_monitoring(self):
        """Inicia o monitoramento do arquivo de diário mais recente."""
        if self.is_running:
            logging.warning("Monitoramento já está em execução.")
            return

        latest_file = get_latest_journal_file(self.JOURNAL_DIR)
        if not latest_file:
            logging.error("Nenhum arquivo de diário encontrado para monitorar.")
            return

        self.event_handler = JournalFileMonitor(latest_file, self.process_event)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, os.path.dirname(latest_file), recursive=False)
        self.observer.start()
        self.is_running = True
        logging.info("Monitoramento iniciado.")

        # Inicia o monitoramento EDDN em uma thread separada
        # self.eddn_thread = threading.Thread(target=start_eddn_monitoring, args=(self.process_event,))
        # self.eddn_thread.daemon = True
        # self.eddn_thread.start()

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
    # Exemplo de uso (apenas para teste)
    core = BackendCore(JOURNAL_DIR)
    core.start_monitoring()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        core.stop_monitoring()
