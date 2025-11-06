import sys
import os
import logging
import threading
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QLabel, QListWidget, QStackedWidget, QFileDialog,
    QMessageBox, QListWidgetItem, QGridLayout, QProgressBar
)
from PySide6.QtCore import QObject, Signal, Slot, QThread, Qt
from PySide6.QtGui import QFont

# Adiciona o diretório do backend ao path para importação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

# Importa o core do backend
from main import BackendCore, JOURNAL_DIR, DB_CONFIG
from csv_exporter import CSVExporter
from backend.rank_data import RANK_NAMES, PILOTS__FEDERATION_RANKS, SUPERPOWER_RANKS

# --- Classes de Visualização (Views) ---

class ConfigView(QWidget):
    """Visualização para configurar o MySQL e o caminho do Journal."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

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
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.journal_path_input)
        path_layout.addWidget(self.browse_button)
        layout.addLayout(path_layout)
        
        self.save_config_button = QPushButton("Salvar Configurações e Testar Conexão")
        layout.addWidget(self.save_config_button)

        layout.addStretch()

class ControlView(QWidget):
    """Visualização para controlar o monitoramento e exportação."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.status_label = QLabel("Status: Parado")
        self.status_label.setStyleSheet("font-weight: bold; color: blue;")
        layout.addWidget(self.status_label)

        self.start_button = QPushButton("Iniciar Monitoramento")
        self.start_button.setEnabled(False) # Desabilitado até a configuração ser salva

        self.stop_button = QPushButton("Parar Monitoramento")
        self.stop_button.setEnabled(False)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.start_button)
        h_layout.addWidget(self.stop_button)
        layout.addLayout(h_layout)

        self.export_button = QPushButton("Exportar Dados para CSV")
        self.export_button.setEnabled(True)
        layout.addWidget(self.export_button)

        layout.addStretch()

class PilotRanksView(QWidget):
    """Visualização para exibir o status e progresso dos ranques do piloto."""
    def __init__(self, backend_core, parent=None):
        super().__init__(parent)
        self.backend_core = backend_core
        self.rank_labels = {}
        self.progress_bars = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Status de Ranques do Piloto")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        self.update_button = QPushButton("Atualizar Ranques")
        layout.addWidget(self.update_button)
        
        self.grid_layout = QGridLayout()
        
        # Cabeçalhos
        self.grid_layout.addWidget(QLabel("Tipo de Ranque"), 0, 0, Qt.AlignmentFlag.AlignLeft)
        self.grid_layout.addWidget(QLabel("Ranque Atual"), 0, 1, Qt.AlignmentFlag.AlignLeft)
        self.grid_layout.addWidget(QLabel("Progresso para o Próximo"), 0, 2, Qt.AlignmentFlag.AlignLeft)
        
        row = 1
        for rank_type in PILOTS__FEDERATION_RANKS + SUPERPOWER_RANKS:
            # Label do Tipo de Ranque
            self.grid_layout.addWidget(QLabel(rank_type), row, 0, Qt.AlignmentFlag.AlignLeft)
            
            # Label do Ranque Atual
            self.rank_labels[rank_type] = QLabel("N/A")
            self.grid_layout.addWidget(self.rank_labels[rank_type], row, 1, Qt.AlignmentFlag.AlignLeft)
            
            # Barra de Progresso
            self.progress_bars[rank_type] = QProgressBar()
            self.progress_bars[rank_type].setFormat("%p%")
            self.progress_bars[rank_type].setValue(0)
            self.grid_layout.addWidget(self.progress_bars[rank_type], row, 2)
            
            row += 1
            
        layout.addLayout(self.grid_layout)
        layout.addStretch()
        
        self.update_button.clicked.connect(self.update_ranks_display)

    @Slot()
    def update_ranks_display(self):
        conn = self.backend_core.get_db_connection('db_piloto')
        if not conn:
            QMessageBox.critical(self, "Erro de Conexão", "Não foi possível conectar ao banco de dados para buscar os ranques.")
            return

        try:
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT rank_type, rank_value, rank_progress FROM pilot_ranks"
            cursor.execute(sql)
            ranks_data = {row['rank_type']: row for row in cursor.fetchall()}
            
            for rank_type in PILOTS__FEDERATION_RANKS + SUPERPOWER_RANKS:
                data = ranks_data.get(rank_type)
                
                if data:
                    rank_value = data['rank_value']
                    progress = data['rank_progress'] # 0.0 a 1.0
                    
                    # Ranque Atual (Nome)
                    rank_name = RANK_NAMES.get(rank_type, ["N/A"])[rank_value]
                    self.rank_labels[rank_type].setText(rank_name)
                    
                    # Progresso (Barra)
                    progress_percent = int(progress * 100)
                    self.progress_bars[rank_type].setValue(progress_percent)
                    
                    # Para ranques de Superpotência, o progresso é apenas o percentual para o próximo nível
                    if rank_type in SUPERPOWER_RANKS:
                        self.progress_bars[rank_type].setFormat(f"{progress_percent}% para {RANK_NAMES[rank_type][rank_value + 1] if rank_value + 1 < len(RANK_NAMES[rank_type]) else 'Máximo'}")
                    else:
                        self.progress_bars[rank_type].setFormat(f"{progress_percent}%")
                else:
                    self.rank_labels[rank_type].setText("N/A")
                    self.progress_bars[rank_type].setValue(0)
                    self.progress_bars[rank_type].setFormat("N/A")
                    
        except Exception as e:
            QMessageBox.critical(self, "Erro de Consulta", f"Erro ao buscar dados de ranques: {e}")
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

# --- Handlers e Workers ---

class LogSignalHandler(logging.Handler, QObject):
    log_record_signal = Signal(str)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        logging.Handler.__init__(self)
        self.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    def emit(self, record):
        msg = self.format(record)
        self.log_record_signal.emit(msg)

class BackendWorker(QObject):
    finished = Signal()
    error = Signal(str)

    def __init__(self, backend_core):
        super().__init__()
        self.backend_core = backend_core

    @Slot()
    def run(self):
        try:
            self.backend_core.start_monitoring()
        except Exception as e:
            self.error.emit(f"Erro fatal no backend: {e}")
        finally:
            self.finished.emit()

class CSVExportWorker(QObject):
    finished = Signal()
    error = Signal(str)

    def __init__(self, db_config, output_dir):
        super().__init__()
        self.db_config = db_config
        self.output_dir = output_dir

    @Slot()
    def run(self):
        try:
            exporter = CSVExporter(self.db_config)
            exporter.export_all_data(self.output_dir)
        except Exception as e:
            self.error.emit(f"Erro durante a exportação CSV: {e}")
        finally:
            self.finished.emit()

# --- Janela Principal ---

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Elite Dangerous Log Tracker (EDLT)")
        self.setGeometry(100, 100, 900, 700)
        
        self.log_handler = LogSignalHandler()
        self.log_handler.log_record_signal.connect(self.update_log_viewer)
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.INFO)

        self.backend_core = BackendCore(DB_CONFIG, JOURNAL_DIR)
        self.backend_thread = None
        self.backend_worker = None

        self.setup_ui()
        self.connect_signals()
        
        self.update_status("Pronto para configurar e iniciar.")

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Menu Lateral
        self.nav_menu = QListWidget()
        self.nav_menu.setFixedWidth(150)
        self.main_layout.addWidget(self.nav_menu)

        # Conteúdo Empilhado (Stacked Widget)
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        # Adiciona as visualizações
        self.config_view = ConfigView()
        self.control_view = ControlView()
        self.pilot_ranks_view = PilotRanksView(self.backend_core) # Nova Visualização
        
        self.stacked_widget.addWidget(self.config_view)
        self.stacked_widget.addWidget(self.control_view)
        self.stacked_widget.addWidget(self.pilot_ranks_view) # Adiciona a nova visualização

        self.nav_menu.addItem("Configuração")
        self.nav_menu.addItem("Controle")
        self.nav_menu.addItem("Ranques do Piloto") # Adiciona item ao menu

        # Log Viewer (agora parte do layout principal)
        log_layout = QVBoxLayout()
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        log_layout.addWidget(QLabel("Log de Eventos:"))
        log_layout.addWidget(self.log_viewer)
        self.main_layout.addLayout(log_layout)

    def connect_signals(self):
        self.nav_menu.currentRowChanged.connect(self.stacked_widget.setCurrentIndex)
        
        # Sinais da ConfigView
        self.config_view.browse_button.clicked.connect(self.browse_journal_path)
        self.config_view.save_config_button.clicked.connect(self.save_config)

        # Sinais da ControlView
        self.control_view.start_button.clicked.connect(self.start_monitoring)
        self.control_view.stop_button.clicked.connect(self.stop_monitoring)
        self.control_view.export_button.clicked.connect(self.prompt_csv_export)

    @Slot(str)
    def update_log_viewer(self, text):
        self.log_viewer.append(text)

    def update_status(self, text, is_running=False):
        self.control_view.status_label.setText(f"Status: {text}")
        if is_running:
            self.control_view.status_label.setStyleSheet("font-weight: bold; color: green;")
        else:
            self.control_view.status_label.setStyleSheet("font-weight: bold; color: blue;")

    def browse_journal_path(self):
        directory = QFileDialog.getExistingDirectory(self, "Selecione o Diretório do Elite Dangerous Journal")
        if directory:
            self.config_view.journal_path_input.setText(directory)

    def save_config(self):
        new_db_config = {
            "host": self.config_view.mysql_host.text(),
            "user": self.config_view.mysql_user.text(),
            "password": self.config_view.mysql_pass.text(),
        }
        new_journal_dir = self.config_view.journal_path_input.text()
        
        temp_core = BackendCore(new_db_config, new_journal_dir)
        
        conn = temp_core.get_db_connection("db_piloto")
        if conn:
            QMessageBox.information(self, "Configuração Salva", "Conexão com o MySQL bem-sucedida! Configurações salvas.")
            conn.close()
            
            self.backend_core = temp_core
            self.control_view.start_button.setEnabled(True)
            self.update_status("Configuração salva. Pronto para iniciar o monitoramento.")
        else:
            QMessageBox.critical(self, "Erro de Conexão", "Falha ao conectar ao MySQL. Verifique as credenciais e se o servidor está rodando.")
            self.control_view.start_button.setEnabled(False)

    def start_monitoring(self):
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
        
        self.control_view.start_button.setEnabled(False)
        self.control_view.stop_button.setEnabled(True)
        self.update_status("Monitoramento em execução...", is_running=True)
        logging.info("GUI: Monitoramento iniciado.")

    def stop_monitoring(self):
        if not self.backend_core.is_running:
            return
            
        self.backend_core.stop_monitoring()
        
        if self.backend_thread and self.backend_thread.isRunning():
            self.backend_thread.quit()
            self.backend_thread.wait(2000)

        self.control_view.start_button.setEnabled(True)
        self.control_view.stop_button.setEnabled(False)
        self.update_status("Monitoramento parado.")
        logging.info("GUI: Monitoramento parado.")

    def prompt_csv_export(self):
        if not self.backend_core.DB_CONFIG.get("user"):
            QMessageBox.warning(self, "Configuração Pendente", "Salve as configurações do MySQL antes de exportar.")
            return

        export_dir = QFileDialog.getExistingDirectory(self, "Selecione o Diretório de Destino para CSV")
        if not export_dir:
            return

        self.control_view.export_button.setEnabled(False)
        self.update_status("Exportando dados para CSV...")
        
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
        self.control_view.export_button.setEnabled(True)
        self.update_status("Exportação CSV concluída.", is_running=self.backend_core.is_running)
        QMessageBox.information(self, "Exportação Concluída", "Todos os dados foram exportados para CSV com sucesso!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
