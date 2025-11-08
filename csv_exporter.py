import csv
import os
import logging
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CSVExporter:
    def __init__(self, db_path):
        self.DB_PATH = db_path

    def get_db_connection(self):
        """Cria e retorna uma conexão com o banco de dados SQLite."""
        try:
            conn = sqlite3.connect(self.DB_PATH)
            conn.row_factory = sqlite3.Row # Permite acessar colunas por nome
            return conn
        except sqlite3.Error as e:
            logging.error(f"Erro ao conectar ao banco de dados SQLite: {e}")
            return None

    def export_table_to_csv(self, table_name, output_path):
        """Exporta o conteúdo de uma tabela específica para um arquivo CSV."""
        conn = self.get_db_connection()
        if not conn:
            logging.error(f"Não foi possível exportar a tabela {table_name}: Falha na conexão com o DB.")
            return False

        try:
            cursor = conn.cursor()
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)
            
            # Obtém os nomes das colunas
            column_names = [i[0] for i in cursor.description]

            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                
                # Escreve o cabeçalho
                csv_writer.writerow(column_names)
                
                # Escreve as linhas de dados
                for row in cursor:
                    # Converte tipos de dados não-nativos (como None) para string
                    processed_row = [str(item) if item is not None else '' for item in row]
                    csv_writer.writerow(processed_row)

            logging.info(f"Tabela '{table_name}' exportada com sucesso para: {output_path}")
            return True

        except sqlite3.Error as e:
            logging.error(f"Erro ao exportar a tabela {table_name}: {e}")
            return False
        except Exception as e:
            logging.error(f"Erro inesperado durante a exportação: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def export_all_data(self, base_output_dir):
        """Exporta todas as tabelas relevantes para arquivos CSV no diretório especificado."""
        
        # As tabelas são agora todas no mesmo banco de dados SQLite
        all_tables = [
            'journal_events', 
            'pilot_status', 
            'pilot_materials', 
            'pilot_profit', 
            'ship_modules', 
            'system_data'
        ]
        
        exported_files = []
        
        for table_name in all_tables:
            filename = f"{table_name}.csv"
            output_path = os.path.join(base_output_dir, filename)
            
            if self.export_table_to_csv(table_name, output_path):
                exported_files.append(output_path)
        
        return exported_files

if __name__ == '__main__':
    # Exemplo de uso (requer o arquivo edlt.db)
    # from main import SQLITE_DB_PATH
    # exporter = CSVExporter(SQLITE_DB_PATH)
    # output_dir = os.path.expanduser('~/ed_exports')
    # os.makedirs(output_dir, exist_ok=True)
    # exporter.export_all_data(output_dir)
    pass
