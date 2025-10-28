import csv
import os
import logging
from mysql.connector import connect, Error

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CSVExporter:
    def __init__(self, db_config):
        self.DB_CONFIG = db_config

    def get_db_connection(self, db_name):
        """Cria e retorna uma conexão com o banco de dados especificado."""
        try:
            conn = connect(database=db_name, **self.DB_CONFIG)
            return conn
        except Error as e:
            logging.error(f"Erro ao conectar ao banco de dados {db_name}: {e}")
            return None

    def export_table_to_csv(self, db_name, table_name, output_path):
        """Exporta o conteúdo de uma tabela específica para um arquivo CSV."""
        conn = self.get_db_connection(db_name)
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
                    # Converte tipos de dados não-nativos (como datetime) para string
                    processed_row = [str(item) if item is not None else '' for item in row]
                    csv_writer.writerow(processed_row)

            logging.info(f"Tabela '{table_name}' exportada com sucesso para: {output_path}")
            return True

        except Error as e:
            logging.error(f"Erro ao exportar a tabela {table_name}: {e}")
            return False
        except Exception as e:
            logging.error(f"Erro inesperado durante a exportação: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    def export_all_data(self, base_output_dir):
        """Exporta todas as tabelas relevantes para arquivos CSV no diretório especificado."""
        
        # Tabelas do Piloto
        pilot_tables = ['journal_events', 'pilot_journeys', 'pilot_transactions']
        # Tabelas do Universo
        universe_tables = ['star_systems', 'stations', 'commodity_prices']
        
        all_tables = {
            'db_piloto': pilot_tables,
            'db_universo': universe_tables
        }
        
        exported_files = []
        
        for db_name, tables in all_tables.items():
            for table_name in tables:
                filename = f"{db_name}_{table_name}.csv"
                output_path = os.path.join(base_output_dir, filename)
                
                if self.export_table_to_csv(db_name, table_name, output_path):
                    exported_files.append(output_path)
        
        return exported_files

if __name__ == '__main__':
    # Exemplo de uso (requer MySQL rodando e configurado)
    # from main import DB_CONFIG
    # exporter = CSVExporter(DB_CONFIG)
    # output_dir = os.path.expanduser('~/ed_exports')
    # os.makedirs(output_dir, exist_ok=True)
    # exporter.export_all_data(output_dir)
    pass

