import os
import json
import time
import logging
import threading
import sqlite3
import hashlib
from typing import Optional, Dict, Any, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Variáveis de Configuração
JOURNAL_DIR = os.path.expanduser('~/Saved Games/Frontier Developments/Elite Dangerous')
SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'edlt.db')

# --- Funções Auxiliares de Arquivo ---

def get_latest_journal_file(directory: str) -> Optional[str]:
    """Encontra o arquivo de diário mais recente no diretório."""
    try:
        files = [os.path.join(directory, f) for f in os.listdir(directory) 
                 if f.startswith('Journal.') and f.endswith('.log')]
        if not files:
            return None
        # O formato do nome do arquivo é 'Journal.YYYY-MM-DDTHHMMSS.XX.log'
        return max(files, key=os.path.getmtime)
    except FileNotFoundError:
        logging.error(f"Diretório de logs não encontrado: {directory}")
        return None
    except Exception as e:
        logging.error(f"Erro ao buscar arquivo de log mais recente: {e}")
        return None


class JournalFileMonitor(FileSystemEventHandler):
    """Manipulador de eventos do Watchdog para monitorar a escrita no arquivo de diário."""
    
    def __init__(self, journal_path: str, event_processor_callback: Callable):
        self.journal_path = journal_path
        self.file_handle = None
        self.event_processor_callback = event_processor_callback
        self.open_file()

    def open_file(self) -> None:
        """Abre o arquivo de diário e move o ponteiro para o final."""
        if self.file_handle:
            try:
                self.file_handle.close()
            except:
                pass
        
        # FIX: Retry logic para race conditions
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.file_handle = open(self.journal_path, 'r', encoding='utf-8')
                self.file_handle.seek(0, os.SEEK_END)
                logging.info(f"Monitorando o arquivo: {self.journal_path}")
                return
            except (IOError, OSError) as e:
                if attempt < max_retries - 1:
                    time.sleep(0.5)
                    logging.warning(f"Tentativa {attempt + 1}/{max_retries} falhou, tentando novamente...")
                else:
                    logging.error(f"Não foi possível abrir após {max_retries} tentativas: {e}")
                    self.file_handle = None

    def on_modified(self, event):
        """Chamado quando o arquivo de diário é modificado."""
        if event.src_path == self.journal_path and not event.is_directory:
            self.read_new_lines()

    # FIX: Detectar novos arquivos de journal
    def on_created(self, event):
        """Chamado quando um novo arquivo é criado."""
        if (not event.is_directory and 
            event.src_path.endswith('.log') and 
            'Journal.' in os.path.basename(event.src_path)):
            
            new_file = event.src_path
            if os.path.getmtime(new_file) > os.path.getmtime(self.journal_path):
                logging.info(f"Novo arquivo de journal detectado: {new_file}")
                self.journal_path = new_file
                self.open_file()

    def read_new_lines(self) -> None:
        """Lê e processa as novas linhas adicionadas ao arquivo."""
        if not self.file_handle:
            self.open_file()
            if not self.file_handle:
                return

        try:
            new_data = self.file_handle.readlines()
        except (IOError, OSError) as e:
            logging.error(f"Erro ao ler arquivo: {e}")
            self.open_file()
            return
        
        for line in new_data:
            try:
                # FIX: Validação aprimorada de JSON
                line = line.strip()
                if not line:
                    continue
                    
                event_data = json.loads(line)
                
                # FIX: Validar estrutura básica do evento
                if not isinstance(event_data, dict):
                    logging.warning(f"Evento não é um objeto JSON válido: {line[:50]}")
                    continue
                
                if 'event' not in event_data or 'timestamp' not in event_data:
                    logging.warning(f"Evento sem campos obrigatórios (event/timestamp): {line[:50]}")
                    continue
                
                self.event_processor_callback(event_data)
                
            except json.JSONDecodeError as e:
                logging.error(f"Erro ao decodificar JSON: {e} na linha: {line[:100]}")
            except Exception as e:
                logging.error(f"Erro desconhecido ao processar linha: {e}")

    def stop(self) -> None:
        """Fecha o handle do arquivo."""
        if self.file_handle:
            try:
                self.file_handle.close()
            except:
                pass


# --- Core do Backend ---

class BackendCore:
    def __init__(self, journal_dir: str):
        self.JOURNAL_DIR = journal_dir
        self.observer = None
        self.event_handler = None
        self.monitoring_thread = None
        self.is_running = False
        self.db_path = SQLITE_DB_PATH
        self.event_count = 0  # FIX: Contador para logging menos verboso
        self.initialize_db()

    # --- Funções de Banco de Dados (SQLite) ---

    def get_db_connection(self) -> Optional[sqlite3.Connection]:
        """Cria e retorna uma conexão com o banco de dados SQLite."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            conn.row_factory = sqlite3.Row
            # FIX: Ativar WAL mode para melhor concorrência
            conn.execute("PRAGMA journal_mode=WAL")
            return conn
        except sqlite3.Error as e:
            logging.error(f"Erro ao conectar ao banco de dados SQLite: {e}")
            return None

    def initialize_db(self) -> None:
        """Cria as tabelas se não existirem."""
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            schema_path = os.path.join(os.path.dirname(__file__), 'sqlite_schema.sql')
            with open(schema_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            conn.executescript(sql_script)
            conn.commit()
            logging.info("Banco de dados SQLite inicializado com sucesso.")
        except FileNotFoundError:
            logging.error(f"Arquivo de schema não encontrado: {schema_path}")
        except Exception as e:
            logging.error(f"Erro ao inicializar o banco de dados SQLite: {e}")
        finally:
            if conn:
                conn.close()

    def _insert_journal_event(self, conn: sqlite3.Connection, event_data: Dict[str, Any]) -> Optional[int]:
        """Insere o evento JSON bruto na tabela journal_events (usa conexão existente)."""
        try:
            cursor = conn.cursor()
            
            timestamp = event_data.get('timestamp')
            event_type = event_data.get('event')
            event_json_str = json.dumps(event_data, ensure_ascii=False)
            
            # FIX: Hash do JSON completo para melhor detecção de duplicatas
            unique_str = f"{timestamp}{event_type}{event_json_str}"
            event_hash = hashlib.sha256(unique_str.encode('utf-8')).hexdigest()

            sql = """
            INSERT OR IGNORE INTO journal_events (timestamp, event_type, event_data, event_hash)
            VALUES (?, ?, ?, ?)
            """
            
            cursor.execute(sql, (timestamp, event_type, event_json_str, event_hash))
            
            if cursor.rowcount > 0:
                # FIX: Logging menos verboso
                self.event_count += 1
                if self.event_count % 10 == 0:
                    logging.info(f"{self.event_count} eventos processados (último: '{event_type}')")
                return cursor.lastrowid
            else:
                return None  # Evento duplicado

        except sqlite3.Error as e:
            logging.error(f"Erro ao inserir evento no SQLite: {e}")
            raise

    def _update_pilot_status(self, conn: sqlite3.Connection, event_data: Dict[str, Any]) -> None:
        """Atualiza o status do piloto (usa conexão existente)."""
        try:
            cursor = conn.cursor()
            
            pilot_name = event_data.get('Commander', 'CMDR_Unknown')
            
            cursor.execute("INSERT OR IGNORE INTO pilot_status (pilot_name, last_update) VALUES (?, ?)", 
                          (pilot_name, event_data.get('timestamp')))
            
            update_fields = {}
            
            event_type = event_data.get('event')
            
            # Ranques
            if event_type == 'Rank':
                for rank_type in ['Combat', 'Trade', 'Explore', 'CQC', 'Federation', 'Empire']:
                    if rank_type in event_data:
                        update_fields[f'rank_{rank_type.lower()}'] = event_data[rank_type]
            
            # Progresso - FIX: Validação de limites
            elif event_type == 'Progress':
                for rank_type in ['Combat', 'Trade', 'Explore', 'CQC', 'Federation', 'Empire']:
                    if rank_type in event_data:
                        progress = min(max(event_data[rank_type] / 100.0, 0.0), 1.0)
                        update_fields[f'progress_{rank_type.lower()}'] = progress
            
            # Localização
            elif event_type in ['Location', 'FSDJump']:
                update_fields['system_name'] = event_data.get('StarSystem')
                update_fields['station_name'] = event_data.get('StationName')
                
            # Ship
            elif event_type in ['Loadout', 'ShipyardSwap']:
                update_fields['ship_id'] = event_data.get('ShipID')
                update_fields['ship_name'] = event_data.get('ShipName')
                update_fields['ship_model'] = event_data.get('Ship')
            
            if update_fields:
                update_fields['last_update'] = event_data.get('timestamp')
                
                set_clause = ", ".join([f"{k} = ?" for k in update_fields.keys()])
                params = list(update_fields.values())
                params.append(pilot_name)
                
                sql = f"UPDATE pilot_status SET {set_clause} WHERE pilot_name = ?"
                cursor.execute(sql, params)

        except sqlite3.Error as e:
            logging.error(f"Erro ao atualizar status do piloto: {e}")
            raise

    def _update_pilot_materials(self, conn: sqlite3.Connection, event_data: Dict[str, Any]) -> None:
        """Atualiza o inventário de materiais (usa conexão existente)."""
        if event_data.get('event') != 'Materials':
            return
            
        try:
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM pilot_materials")
            
            materials = (event_data.get('Raw', []) + 
                        event_data.get('Manufactured', []) + 
                        event_data.get('Encoded', []))
            
            for material in materials:
                name = material.get('Name')
                count = material.get('Count', 0)
                category = material.get('Category', 'Unknown')
                
                if name and count >= 0:
                    sql = "INSERT INTO pilot_materials (material_name, category, count) VALUES (?, ?, ?)"
                    cursor.execute(sql, (name, category, count))

        except sqlite3.Error as e:
            logging.error(f"Erro ao atualizar inventário de materiais: {e}")
            raise

    def _insert_pilot_profit(self, conn: sqlite3.Connection, event_data: Dict[str, Any], 
                            profit_type: str, amount: int) -> None:
        """Insere um registro de lucro (usa conexão existente)."""
        try:
            cursor = conn.cursor()
            sql = "INSERT INTO pilot_profit (timestamp, profit_type, amount) VALUES (?, ?, ?)"
            cursor.execute(sql, (event_data.get('timestamp'), profit_type, amount))

        except sqlite3.Error as e:
            logging.error(f"Erro ao inserir lucro: {e}")
            raise

    def _update_system_data(self, conn: sqlite3.Connection, event_data: Dict[str, Any]) -> None:
        """Atualiza dados do sistema (usa conexão existente)."""
        try:
            cursor = conn.cursor()
            event_type = event_data.get('event')
            system_name = event_data.get('StarSystem')
            
            if not system_name:
                return

            if event_type == 'FSDJump':
                cursor.execute("DELETE FROM system_data WHERE system_name != ?", (system_name,))
                
            if event_type in ['FSDJump', 'Location'] and 'Body' in event_data:
                star_name = event_data.get('Body')
                star_data = json.dumps(event_data, ensure_ascii=False)
                
                sql = "INSERT OR REPLACE INTO system_data (name, system_name, type, distance_ls, data_json) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(sql, (star_name, system_name, 'STAR', 0.0, star_data))
                
                if event_data.get('StationName'):
                    station_name = event_data.get('StationName')
                    cursor.execute(sql, (station_name, system_name, 'STATION', None, star_data))
                    
            elif event_type == 'Scan':
                body_name = event_data.get('BodyName')
                body_type = event_data.get('BodyType', 'Unknown')
                distance = event_data.get('DistanceFromArrivalLS')
                
                sql = "INSERT OR REPLACE INTO system_data (name, system_name, type, distance_ls, data_json) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(sql, (body_name, system_name, body_type, distance, 
                                   json.dumps(event_data, ensure_ascii=False)))
                
            elif event_type == 'FSSSignalDiscovered':
                signal_name = event_data.get('SignalName')
                
                sql = "INSERT OR REPLACE INTO system_data (name, system_name, type, distance_ls, data_json) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(sql, (signal_name, system_name, 'SIGNAL', None, 
                                   json.dumps(event_data, ensure_ascii=False)))

        except sqlite3.Error as e:
            logging.error(f"Erro ao atualizar dados do sistema: {e}")
            raise

    def _update_ship_modules(self, conn: sqlite3.Connection, event_data: Dict[str, Any]) -> None:
        """Atualiza o loadout da nave (usa conexão existente)."""
        if event_data.get('event') != 'Loadout':
            return
            
        try:
            cursor = conn.cursor()
            ship_id = event_data.get('ShipID')
            
            cursor.execute("DELETE FROM ship_modules WHERE ship_id = ?", (ship_id,))
            
            modules = event_data.get('Modules', [])
            
            for module in modules:
                slot = module.get('Slot')
                item = module.get('Item')
                health = min(max(module.get('Health', 1.0), 0.0), 1.0)  # FIX: Validar range
                
                if slot and item:
                    sql = "INSERT INTO ship_modules (ship_id, slot, module, health) VALUES (?, ?, ?, ?)"
                    cursor.execute(sql, (ship_id, slot, item, health))

        except sqlite3.Error as e:
            logging.error(f"Erro ao atualizar módulos da nave: {e}")
            raise

    # FIX: Usar uma única transação para processar eventos
    def process_event(self, event_data: Dict[str, Any]) -> None:
        """Processa um evento do diário e o insere no banco de dados."""
        
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            conn.execute("BEGIN TRANSACTION")
            
            event_id = self._insert_journal_event(conn, event_data)
            if event_id is None:
                conn.rollback()
                return  # Evento duplicado

            event_type = event_data.get('event')

            self._update_pilot_status(conn, event_data)
            
            # Processar lucros
            if event_type == 'MarketSell':
                profit = event_data.get('SellPrice', 0) * event_data.get('Count', 0)
                self._insert_pilot_profit(conn, event_data, 'TRADE', profit)
            elif event_type == 'Bounty':
                self._insert_pilot_profit(conn, event_data, 'BOUNTY', event_data.get('Reward', 0))
            elif event_type == 'MultiSellExplorationData':
                self._insert_pilot_profit(conn, event_data, 'EXPLORATION', event_data.get('TotalEarnings', 0))
            elif event_type == 'SellOrganicData':
                self._insert_pilot_profit(conn, event_data, 'EXOBIOLOGY', event_data.get('TotalEarnings', 0))
                
            if event_type == 'Materials':
                self._update_pilot_materials(conn, event_data)
                
            if event_type in ['FSDJump', 'Location', 'Scan', 'FSSSignalDiscovered']:
                self._update_system_data(conn, event_data)
                
            if event_type == 'Loadout':
                self._update_ship_modules(conn, event_data)

            conn.commit()
            
        except sqlite3.Error as e:
            conn.rollback()
            logging.error(f"Erro ao processar evento '{event_data.get('event')}': {e}")
        except Exception as e:
            conn.rollback()
            logging.error(f"Erro inesperado ao processar evento: {e}")
        finally:
            if conn:
                conn.close()

    # --- Funções de Controle ---

    def start_monitoring(self) -> None:
        """Inicia o monitoramento do arquivo de diário mais recente."""
        if self.is_running:
            logging.warning("Monitoramento já está em execução.")
            return

        # FIX: Limpar observer anterior se existir
        if self.observer:
            try:
                self.observer.stop()
                self.observer.join(timeout=2.0)
            except:
                pass
            self.observer = None

        latest_file = get_latest_journal_file(self.JOURNAL_DIR)
        if not latest_file:
            logging.error("Nenhum arquivo de diário encontrado para monitorar.")
            return

        self.event_handler = JournalFileMonitor(latest_file, self.process_event)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, os.path.dirname(latest_file), recursive=False)
        self.observer.start()
        self.is_running = True
        self.event_count = 0  # Reset contador
        logging.info("Monitoramento iniciado.")

    def stop_monitoring(self) -> None:
        """Para o monitoramento."""
        if self.observer:
            try:
                self.observer.stop()
                self.observer.join(timeout=2.0)
            except Exception as e:
                logging.error(f"Erro ao parar observer: {e}")
            
        if self.event_handler:
            self.event_handler.stop()
        
        self.is_running = False
        logging.info(f"Monitoramento parado. Total de eventos processados: {self.event_count}")


if __name__ == '__main__':
    core = BackendCore(JOURNAL_DIR)
    core.start_monitoring()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        core.stop_monitoring()
