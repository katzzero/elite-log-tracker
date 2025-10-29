import sys
import os
import logging
import threading
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QLabel, QTabWidget, QFileDialog,
    QMessageBox
)
from PySide6.QtCore import QObject, Signal, Slot, QThread, Qt

# Adiciona o diretório do backend ao path para importação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

# Importa o core do backend
from main import BackendCore, JOURNAL_DIR, DB_CONFIG
from csv_exporter import CSVExporter

# Configuração de Logging para capturar logs no GUI
class LogSignalHandler(logging.Handler, QObject):
    """Handler de log que emite um sinal para o GUI."""
    log_record_signal = Signal(str)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        logging.Handler.__init__(self)
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    def emit(self, record):
        msg = self.format(record)
        self.log_record_signal.emit(msg)

class BackendWorker(QObject):
    """Worker para rodar o BackendCore em uma thread separada."""
    
    finished = Signal()
    error = Signal(str)

    def __init__(self, backend_core):
        super().__init__()
        self.backend_core = backend_core

    @Slot()
    def run(self):
        """Inicia o monitoramento do backend."""
        try:
            self.backend_core.start_monitoring()
        except Exception as e:
            self.error.emit(f"Erro fatal no backend: {e}")
        finally:
            self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Elite Dangerous Log Tracker (EDLT)")
        self.setGeometry(100, 100, 800, 600)
        
        # Configura o logger para a GUI
        self.log_handler = LogSignalHandler()
        self.log_handler.log_record_signal.connect(self.update_log_viewer)
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.INFO)

        # Inicializa o Core do Backend (com configurações padrão/placeholder)
        self.backend_core = BackendCore(DB_CONFIG, JOURNAL_DIR)
        self.backend_thread = None
        self.backend_worker = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        self.setup_config_tab()
        self.setup_control_tab()

        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.main_layout.addWidget(QLabel("Log de Eventos:"))
        self.main_layout.addWidget(self.log_viewer)
        
        self.update_status("Pronto para configurar e iniciar.")

    def setup_config_tab(self):
        config_widget = QWidget()
        layout = QVBoxLayout(config_widget)

        # Configuração do MySQL
        layout.addWidget(QLabel("--- Configuração MySQL ---"))
        self.mysql_host = QLineEdit("localhost")
        self.mysql_user = QLineEdit("ed_user")
        self.mysql_pass = QLineEdit("ed_password")
        
        layout.addWidget(QLabel("Host:"))
        layout.addWidget(self.mysql_host)
        layout.addWidget(QLabel("Usuário:"))
        layout.addWidget(self.mysql_user)
        layout.addWidget(QLabel("Senha:"))
        layout.addWidget(self.mysql_pass)

        # Configuração do Journal Path
        layout.addWidget(QLabel("\n--- Caminho do Diário (Journal Path) ---"))
        self.journal_path_input = QLineEdit(JOURNAL_DIR)
        self.journal_path_input.setPlaceholderText("Ex: C:\\Users\\SeuUsuario\\Saved Games\\Frontier Developments\\Elite Dangerous")
        
        self.browse_button = QPushButton("Procurar Diretório")
        self.browse_button.clicked.connect(self.browse_journal_path)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.journal_path_input)
        path_layout.addWidget(self.browse_button)
        layout.addLayout(path_layout)
        
        self.save_config_button = QPushButton("Salvar Configurações e Testar Conexão")
        self.save_config_button.clicked.connect(self.save_config)
        layout.addWidget(self.save_config_button)

        layout.addStretch()
        self.tab_widget.addTab(config_widget, "Configuração")

    def setup_control_tab(self):
        control_widget = QWidget()
        layout = QVBoxLayout(control_widget)

        self.status_label = QLabel("Status: Parado")
        self.status_label.setStyleSheet("font-weight: bold; color: blue;")
        layout.addWidget(self.status_label)

        self.start_button = QPushButton("Iniciar Monitoramento")
        self.start_button.clicked.connect(self.start_monitoring)
        self.start_button.setEnabled(False) # Desabilitado até a configuração ser salva

        self.stop_button = QPushButton("Parar Monitoramento")
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.stop_button.setEnabled(False)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.start_button)
        h_layout.addWidget(self.stop_button)
        layout.addLayout(h_layout)

        # Botão de Exportar CSV (Implementado na Fase 5)
        self.export_button = QPushButton("Exportar Dados para CSV")
        self.export_button.setEnabled(True)
        self.export_button.clicked.connect(self.prompt_csv_export)
        layout.addWidget(self.export_button)

        layout.addStretch()
        self.tab_widget.addTab(control_widget, "Controle e Status")

    @Slot(str)
    def update_log_viewer(self, text):
        """Atualiza o visualizador de log com novas mensagens."""
        self.log_viewer.append(text)

    def update_status(self, text, is_running=False):
        """Atualiza o label de status."""
        self.status_label.setText(f"Status: {text}")
        if is_running:
            self.status_label.setStyleSheet("font-weight: bold; color: green;")
        else:
            self.status_label.setStyleSheet("font-weight: bold; color: blue;")

    def browse_journal_path(self):
        """Abre a caixa de diálogo para selecionar o diretório do Journal."""
        directory = QFileDialog.getExistingDirectory(self, "Selecione o Diretório do Elite Dangerous Journal")
        if directory:
            self.journal_path_input.setText(directory)

    def save_config(self):
        """Salva as configurações e testa a conexão com o banco de dados."""
        new_db_config = {
            'host': self.mysql_host.text(),
            'user': self.mysql_user.text(),
            'password': self.mysql_pass.text(),
        }
        new_journal_dir = self.journal_path_input.text()
        
        # Cria um novo BackendCore com as novas configurações
        temp_core = BackendCore(new_db_config, new_journal_dir)
        
        # Testa a conexão com o db_piloto (apenas para verificar credenciais)
        conn = temp_core.get_db_connection('db_piloto')
        if conn:
            QMessageBox.information(self, "Configuração Salva", "Conexão com o MySQL bem-sucedida! Configurações salvas.")
            conn.close()
            
            # Atualiza o core principal e habilita o botão Iniciar
            self.backend_core = temp_core
            self.start_button.setEnabled(True)
            self.update_status("Configuração salva. Pronto para iniciar o monitoramento.")
        else:
            QMessageBox.critical(self, "Erro de Conexão", "Falha ao conectar ao MySQL. Verifique as credenciais e se o servidor está rodando.")
            self.start_button.setEnabled(False)

    def start_monitoring(self):
        """Inicia o monitoramento em uma thread separada."""
        if self.backend_core.is_running:
            return

        self.backend_thread = QThread()
        self.backend_worker = BackendWorker(self.backend_core)
        self.backend_worker.moveToThread(self.backend_thread)

        self.backend_thread.started.connect(self.backend_worker.run)
        self.backend_worker.finished.connect(self.backend_thread.quit)
        self.backend_worker.finished.connect(self.backend_worker.deleteLater)
        self.backend_thread.finished.connect(self.backend_thread.deleteLater)
        self.backend_worker.error.connect(lambda e: QMessageBox.critical(self, "Erro de Execução", e))
        
        self.backend_thread.start()
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.update_status("Monitoramento em execução...", is_running=True)
        logging.info("GUI: Monitoramento iniciado.")

    def stop_monitoring(self):
        """Para o monitoramento."""
        if not self.backend_core.is_running:
            return
            
        self.backend_core.stop_monitoring()
        
        # Espera a thread terminar (opcional, mas mais limpo)
        if self.backend_thread and self.backend_thread.isRunning():
            self.backend_thread.quit()
            self.backend_thread.wait(2000) # Espera no máximo 2 segundos

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.update_status("Monitoramento parado.")
        logging.info("GUI: Monitoramento parado.")

    def prompt_csv_export(self):
        """Solicita o diretório e inicia a exportação CSV."""
        if not self.backend_core.DB_CONFIG.get('user'):
            QMessageBox.warning(self, "Configuração Pendente", "Salve as configurações do MySQL na aba 'Configuração' antes de exportar.")
            return

        export_dir = QFileDialog.getExistingDirectory(self, "Selecione o Diretório de Destino para CSV")
        if not export_dir:
            return

        self.export_button.setEnabled(False)
        self.update_status("Exportando dados para CSV...")
        
        # Cria e executa o worker de exportação em uma thread separada
        self.export_thread = QThread()
        self.export_worker = CSVExportWorker(self.backend_core.DB_CONFIG, export_dir)
        self.export_worker.moveToThread(self.export_thread)

        self.export_thread.started.connect(self.export_worker.run)
        self.export_worker.finished.connect(self.export_thread.quit)
        self.export_worker.finished.connect(self.export_finished)
        self.export_worker.finished.connect(self.export_worker.deleteLater)
        self.export_thread.finished.connect(self.export_thread.deleteLater)
        self.export_worker.error.connect(lambda e: QMessageBox.critical(self, "Erro de Exportação", e))
        
        self.export_thread.start()
        
    @Slot()
    def export_finished(self):
        """Chamado quando a exportação CSV termina."""
        self.export_button.setEnabled(True)
        self.update_status("Exportação CSV concluída.", is_running=self.backend_core.is_running)
        QMessageBox.information(self, "Exportação Concluída", "Todos os dados foram exportados para CSV com sucesso!")

class CSVExportWorker(QObject):
    """Worker para rodar a exportação CSV em uma thread separada."""
    
    finished = Signal()
    error = Signal(str)

    def __init__(self, db_config, output_dir):
        super().__init__()
        self.db_config = db_config
        self.output_dir = output_dir

    @Slot()
    def run(self):
        """Executa a exportação CSV."""
        try:
            exporter = CSVExporter(self.db_config)
            exporter.export_all_data(self.output_dir)
        except Exception as e:
            self.error.emit(f"Erro durante a exportação CSV: {e}")
        finally:
            self.finished.emit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

