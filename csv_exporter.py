import csv
import os
import logging
import sqlite3
from typing import Optional, List, Callable

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# FIX: Whitelist de tabelas permitidas para prevenir SQL injection
ALLOWED_TABLES = [
    'journal_events',
    'pilot_status',
    'pilot_materials',
    'pilot_profit',
    'ship_modules',
    'system_data'
]


class CSVExporter:
    def __init__(self, db_path: str):
        self.DB_PATH = db_path

    def get_db_connection(self) -> Optional[sqlite3.Connection]:
        """Cria e retorna uma conexão com o banco de dados SQLite."""
        try:
            conn = sqlite3.connect(self.DB_PATH)
            conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
            return conn
        except sqlite3.Error as e:
            logging.error(f"Erro ao conectar ao banco de dados SQLite: {e}")
            return None

    def export_table_to_csv(self, table_name: str, output_path: str) -> bool:
        """Exporta o conteúdo de uma tabela específica para um arquivo CSV."""
        # FIX: Validação contra SQL injection
        if table_name not in ALLOWED_TABLES:
            logging.error(f"Tabela não permitida para exportação: {table_name}")
            return False

        conn = self.get_db_connection()
        if not conn:
            logging.error(f"Não foi possível exportar a tabela {table_name}: Falha na conexão com o DB.")
            return False

        try:
            cursor = conn.cursor()
            # Agora é seguro usar f-string pois validamos contra whitelist
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)

            # Obtém os nomes das colunas
            column_names = [i[0] for i in cursor.description]

            # FIX: UTF-8-BOM para compatibilidade com Excel no Windows
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                csv_writer = csv.writer(csvfile)
                # Escreve o cabeçalho
                csv_writer.writerow(column_names)

                # Escreve as linhas de dados
                row_count = 0
                for row in cursor:
                    # Converte tipos de dados não-nativos (como None) para string
                    processed_row = [str(item) if item is not None else '' for item in row]
                    csv_writer.writerow(processed_row)
                    row_count += 1

            logging.info(f"Tabela '{table_name}' exportada com sucesso: {row_count} linhas para {output_path}")
            return True

        except sqlite3.Error as e:
            logging.error(f"Erro ao exportar a tabela {table_name}: {e}")
            return False
        except IOError as e:
            logging.error(f"Erro de I/O ao escrever arquivo CSV: {e}")
            return False
        except Exception as e:
            logging.error(f"Erro inesperado durante a exportação: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def export_all_data(self, base_output_dir: str, progress_callback: Optional[Callable[[int], None]] = None) -> List[str]:
        """Exporta todas as tabelas relevantes para arquivos CSV no diretório especificado.

        Args:
            base_output_dir: Diretório onde os arquivos CSV serão salvos
            progress_callback: Função opcional que recebe o percentual de progresso (0-100)

        Returns:
            Lista com os caminhos dos arquivos exportados com sucesso
        """
        if not os.path.exists(base_output_dir):
            try:
                os.makedirs(base_output_dir, exist_ok=True)
            except OSError as e:
                logging.error(f"Não foi possível criar diretório de saída: {e}")
                return []

        exported_files = []
        total_tables = len(ALLOWED_TABLES)

        for index, table_name in enumerate(ALLOWED_TABLES):
            filename = f"{table_name}.csv"
            output_path = os.path.join(base_output_dir, filename)

            if self.export_table_to_csv(table_name, output_path):
                exported_files.append(output_path)

            # FIX: Emitir progresso após cada tabela exportada
            if progress_callback:
                progress_percent = int(((index + 1) / total_tables) * 100)
                progress_callback(progress_percent)

        logging.info(f"Exportação concluída: {len(exported_files)}/{len(ALLOWED_TABLES)} tabelas exportadas.")
        return exported_files


if __name__ == '__main__':
    # Exemplo de uso (requer o arquivo edlt.db)
    # exporter = CSVExporter('edlt.db')
    # output_dir = os.path.expanduser('~/ed_exports')
    # exporter.export_all_data(output_dir)
    pass
