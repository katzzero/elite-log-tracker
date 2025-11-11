import sys
import os

# ============================================================================
# VERIFICAÇÃO DE DEPENDÊNCIAS
# ============================================================================
def check_and_handle_dependencies():
    """Verifica dependências críticas antes de iniciar o aplicativo."""
    missing = []

    # Verifica PySide6
    try:
        import PySide6
    except ImportError:
        missing.append('PySide6')

    # Verifica watchdog
    try:
        import watchdog
    except ImportError:
        missing.append('watchdog')

    if missing:
        print("=" * 70)
        print("ERRO: Dependências não encontradas")
        print("=" * 70)
        print("\nOs seguintes módulos são necessários mas não estão instalados:\n")
        for module in missing:
            print(f"  - {module}")
        print("\n" + "-" * 70)
        print("Para instalar, execute:\n")
        print(f"  pip install {' '.join(missing)}")
        print("\nOu instale todas as dependências:")
        print("  pip install -r requirements.txt")
        print("=" * 70)

        # Tenta mostrar diálogo gráfico se PySide6 estiver disponível
        if 'PySide6' not in missing:
            try:
                from PySide6.QtWidgets import QApplication, QMessageBox
                app = QApplication(sys.argv)
                QMessageBox.critical(
                    None,
                    "Elite Dangerous Log Tracker - Erro de Dependências",
                    f"Módulos necessários não encontrados:\n\n" +
                    "\n".join([f"• {m}" for m in missing]) +
                    f"\n\nPara instalar, execute:\n\npip install {' '.join(missing)}",
                    QMessageBox.Ok
                )
            except:
                pass

        sys.exit(1)

# Executar verificação de dependências antes de importar qualquer módulo
check_and_handle_dependencies()

# ============================================================================
# IMPORTS
# ============================================================================

import logging
import threading
import sqlite3
from typing import Optional
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QLabel, QListWidget, QStackedWidget, QFileDialog,
    QMessageBox, QListWidgetItem, QGridLayout, QProgressBar
)
from PySide6.QtCore import QObject, Signal, Slot, QThread, Qt
from PySide6.QtGui import QFont

# Adiciona o diretório do backend ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

# Importa o core do backend
from main import BackendCore, JOURNAL_DIR, SQLITE_DB_PATH
from csv_exporter import CSVExporter
from backend.rank_data import RANK_NAMES, PILOTS_FEDERATION_RANKS, SUPERPOWER_RANKS
from backend.material_limits import MATERIAL_LIMITS

# FIX: Combinar as listas de ranks
ALL_RANK_TYPES = PILOTS_FEDERATION_RANKS + SUPERPOWER_RANKS

# --- Classes de Visualização (Views) ---

class ConfigView(QWidget):
    """Visualização para configurar o caminho do Journal."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("--- Caminho do Diário (Journal Path) ---"))
        self.journal_path_input = QLineEdit(JOURNAL_DIR)
        self.journal_path_input.setPlaceholderText(
            "Ex: C:\\Users\\SeuUsuario\\Saved Games\\Frontier Developments\\Elite Dangerous"
        )
        
        self.browse_button = QPushButton("Procurar Diretório")
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.journal_path_input)
        path_layout.addWidget(self.browse_button)
        layout.addLayout(path_layout)
        
        self.save_config_button = QPushButton("Salvar Configurações")
        layout.addWidget(self.save_config_button)

        layout.addWidget(QLabel(f"\nBanco de Dados: SQLite ({SQLITE_DB_PATH})"))
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
        self.start_button.setEnabled(False)

        self.stop_button = QPushButton("Parar Monitoramento")
        self.stop_button.setEnabled(False)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.start_button)
        h_layout.addWidget(self.stop_button)
        layout.addLayout(h_layout)

        self.export_button = QPushButton("Exportar Dados para CSV")
        self.export_button.setEnabled(True)
        layout.addWidget(self.export_button)

        # FIX: Indicador de progresso para operações longas
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        layout.addStretch()


class ProfitTrackerView(QWidget):
    """Visualização para exibir o rastreamento de lucro por categoria."""
    def __init__(self, backend_core: BackendCore, parent=None):
        super().__init__(parent)
        self.backend_core = backend_core
        self.profit_labels = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Rastreamento de Lucro (Créditos)")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        self.update_button = QPushButton("Atualizar Lucros")
        layout.addWidget(self.update_button)
        
        self.grid_layout = QGridLayout()
        
        self.grid_layout.addWidget(QLabel("Categoria"), 0, 0, Qt.AlignmentFlag.AlignLeft)
        self.grid_layout.addWidget(QLabel("Total (Cr)"), 0, 1, Qt.AlignmentFlag.AlignRight)
        self.grid_layout.addWidget(QLabel("Total (MCr)"), 0, 2, Qt.AlignmentFlag.AlignRight)
        self.grid_layout.addWidget(QLabel("Total (BCr)"), 0, 3, Qt.AlignmentFlag.AlignRight)
        
        self.categories = ['TRADE', 'BOUNTY', 'EXPLORATION', 'EXOBIOLOGY', 'CARTOGRAPHY']
        self.category_names = {
            'TRADE': 'Comércio',
            'BOUNTY': 'Recompensa (Bounty)',
            'EXPLORATION': 'Exploração (Venda de Dados)',
            'EXOBIOLOGY': 'Exobiologia',
            'CARTOGRAPHY': 'Cartografia (Mapeamento)'
        }
        
        row = 1
        for category in self.categories:
            self.grid_layout.addWidget(QLabel(self.category_names[category]), row, 0, 
                                      Qt.AlignmentFlag.AlignLeft)
            
            self.profit_labels[f'{category}_CR'] = QLabel("0")
            self.profit_labels[f'{category}_MCR'] = QLabel("0.00")
            self.profit_labels[f'{category}_BCR'] = QLabel("0.00")
            
            self.grid_layout.addWidget(self.profit_labels[f'{category}_CR'], row, 1, 
                                      Qt.AlignmentFlag.AlignRight)
            self.grid_layout.addWidget(self.profit_labels[f'{category}_MCR'], row, 2, 
                                      Qt.AlignmentFlag.AlignRight)
            self.grid_layout.addWidget(self.profit_labels[f'{category}_BCR'], row, 3, 
                                      Qt.AlignmentFlag.AlignRight)
            
            row += 1
            
        self.grid_layout.addWidget(QLabel("<b>TOTAL GERAL</b>"), row, 0, 
                                  Qt.AlignmentFlag.AlignLeft)
        self.profit_labels['TOTAL_CR'] = QLabel("<b>0</b>")
        self.profit_labels['TOTAL_MCR'] = QLabel("<b>0.00</b>")
        self.profit_labels['TOTAL_BCR'] = QLabel("<b>0.00</b>")
        
        self.grid_layout.addWidget(self.profit_labels['TOTAL_CR'], row, 1, 
                                  Qt.AlignmentFlag.AlignRight)
        self.grid_layout.addWidget(self.profit_labels['TOTAL_MCR'], row, 2, 
                                  Qt.AlignmentFlag.AlignRight)
        self.grid_layout.addWidget(self.profit_labels['TOTAL_BCR'], row, 3, 
                                  Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(self.grid_layout)
        layout.addStretch()
        
        self.update_button.clicked.connect(self.update_profit_display)

    def format_credits(self, amount: int) -> tuple:
        """Formata o valor em Cr, MCr e BCr."""
        cr = f"{amount:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        mcr = f"{amount / 1_000_000:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        bcr = f"{amount / 1_000_000_000:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return cr, mcr, bcr

    @Slot()
    def update_profit_display(self):
        conn = self.backend_core.get_db_connection()
        if not conn:
            QMessageBox.critical(self, "Erro de Conexão", 
                               "Não foi possível conectar ao banco de dados SQLite.")
            return

        try:
            cursor = conn.cursor()
            sql = "SELECT profit_type, SUM(amount) as total_profit FROM pilot_profit GROUP BY profit_type"
            cursor.execute(sql)
            profit_data = {row['profit_type']: row['total_profit'] for row in cursor.fetchall()}
            
            total_general = 0
            
            for category in self.categories:
                amount = profit_data.get(category, 0)
                total_general += amount
                
                cr, mcr, bcr = self.format_credits(amount)
                
                self.profit_labels[f'{category}_CR'].setText(cr)
                self.profit_labels[f'{category}_MCR'].setText(mcr)
                self.profit_labels[f'{category}_BCR'].setText(bcr)
                
            cr, mcr, bcr = self.format_credits(total_general)
            self.profit_labels['TOTAL_CR'].setText(f"<b>{cr}</b>")
            self.profit_labels['TOTAL_MCR'].setText(f"<b>{mcr}</b>")
            self.profit_labels['TOTAL_BCR'].setText(f"<b>{bcr}</b>")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro de Consulta", f"Erro ao buscar dados de lucro: {e}")
        finally:
            if conn:
                conn.close()


class MaterialsInventoryView(QWidget):
    """Visualização para exibir o inventário de materiais do piloto."""
    def __init__(self, backend_core: BackendCore, parent=None):
        super().__init__(parent)
        self.backend_core = backend_core
        self.table_widget = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Inventário de Materiais (Engenharia e Síntese)")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        self.update_button = QPushButton("Atualizar Inventário")
        layout.addWidget(self.update_button)
        
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Material", "Tipo", "Quantidade", "Capacidade"])
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_widget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.table_widget)
        layout.addStretch()
        
        self.update_button.clicked.connect(self.update_materials_display)

    @Slot()
    def update_materials_display(self):
        conn = self.backend_core.get_db_connection()
        if not conn:
            QMessageBox.critical(self, "Erro de Conexão", 
                               "Não foi possível conectar ao banco de dados SQLite.")
            return

        try:
            cursor = conn.cursor()
            # Seleciona todos os materiais, ordenados por tipo e nome
            sql = "SELECT material_name, material_type, count FROM pilot_materials ORDER BY material_type, material_name"
            cursor.execute(sql)
            materials_data = cursor.fetchall()
            
            self.table_widget.setRowCount(len(materials_data))
            
            for row_num, row_data in enumerate(materials_data):
                material_name, material_type, count = row_data
                
                # 1. Material Name
                self.table_widget.setItem(row_num, 0, QTableWidgetItem(material_name))
                
                # 2. Material Type
                self.table_widget.setItem(row_num, 1, QTableWidgetItem(material_type))
                
                # 3. Quantidade (com barra de progresso)
                # Busca a capacidade máxima do material (se existir)
                max_capacity = MATERIAL_LIMITS.get(material_name, 0)
                
                progress_bar = QProgressBar()
                progress_bar.setRange(0, max_capacity if max_capacity > 0 else 1)
                progress_bar.setValue(count)
                
                # Define a cor da barra de progresso
                if count >= max_capacity and max_capacity > 0:
                    # Vermelho se estiver no limite
                    progress_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
                elif count > max_capacity * 0.8 and max_capacity > 0:
                    # Amarelo se estiver perto do limite
                    progress_bar.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
                else:
                    # Verde
                    progress_bar.setStyleSheet("QProgressBar::chunk { background-color: green; }")
                
                progress_bar.setFormat(f"{count} / {max_capacity}")
                
                self.table_widget.setCellWidget(row_num, 2, progress_bar)
                
                # 4. Capacidade Máxima
                self.table_widget.setItem(row_num, 3, QTableWidgetItem(str(max_capacity)))
                
            self.table_widget.resizeRowsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro de Consulta", f"Erro ao buscar dados de materiais: {e}")
        finally:
            if conn:
                conn.close()

class PilotRanksView(QWidget):
    """Visualização para exibir o status e progresso dos ranques do piloto."""
    def __init__(self, backend_core: BackendCore, parent=None):
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
        
        self.grid_layout.addWidget(QLabel("Tipo de Ranque"), 0, 0, Qt.AlignmentFlag.AlignLeft)
        self.grid_layout.addWidget(QLabel("Ranque Atual"), 0, 1, Qt.AlignmentFlag.AlignLeft)
        self.grid_layout.addWidget(QLabel("Progresso para o Próximo"), 0, 2, 
                                  Qt.AlignmentFlag.AlignLeft)
        
        row = 1
        for rank_type in ALL_RANK_TYPES:
            self.grid_layout.addWidget(QLabel(rank_type), row, 0, Qt.AlignmentFlag.AlignLeft)
            
            self.rank_labels[rank_type] = QLabel("N/A")
            self.grid_layout.addWidget(self.rank_labels[rank_type], row, 1, 
                                      Qt.AlignmentFlag.AlignLeft)
            
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
        conn = self.backend_core.get_db_connection()
        if not conn:
            QMessageBox.critical(self, "Erro de Conexão", 
                               "Não foi possível conectar ao banco de dados SQLite.")
            return

        try:
            cursor = conn.cursor()
            sql = """SELECT rank_combat, progress_combat, rank_trade, progress_trade, 
                     rank_explore, progress_explore, rank_cqc, progress_cqc, 
                     rank_federation, progress_federation, rank_empire, progress_empire 
                     FROM pilot_status LIMIT 1"""
            cursor.execute(sql)
            data = cursor.fetchone()
            
            if data:
                rank_map = {
                    'Combat': ('rank_combat', 'progress_combat'),
                    'Trade': ('rank_trade', 'progress_trade'),
                    'Explore': ('rank_explore', 'progress_explore'),
                    'CQC': ('rank_cqc', 'progress_cqc'),
                    'Federation': ('rank_federation', 'progress_federation'),
                    'Empire': ('rank_empire', 'progress_empire'),
                }
                
                for rank_type, (rank_col, progress_col) in rank_map.items():
                    rank_value = data[rank_col]
                    progress = data[progress_col]
                    
                    rank_names = RANK_NAMES.get(rank_type, ["N/A"])
                    rank_name = rank_names[rank_value] if rank_value < len(rank_names) else "Máximo"
                    self.rank_labels[rank_type].setText(rank_name)
                    
                    progress_percent = int(progress * 100)
                    self.progress_bars[rank_type].setValue(progress_percent)
                    
                    if rank_type in SUPERPOWER_RANKS:
                        next_rank = (rank_names[rank_value + 1] if rank_value + 1 < len(rank_names) 
                                   else 'Máximo')
                        self.progress_bars[rank_type].setFormat(f"{progress_percent}% para {next_rank}")
                    else:
                        self.progress_bars[rank_type].setFormat(f"{progress_percent}%")
            else:
                for rank_type in ALL_RANK_TYPES:
                    self.rank_labels[rank_type].setText("N/A")
                    self.progress_bars[rank_type].setValue(0)
                    self.progress_bars[rank_type].setFormat("N/A")
                    
        except Exception as e:
            QMessageBox.critical(self, "Erro de Consulta", f"Erro ao buscar dados de ranques: {e}")
        finally:
            if conn:
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

    def __init__(self, backend_core: BackendCore):
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
    finished = Signal(list)  # FIX: Retornar lista de arquivos exportados
    error = Signal(str)
    progress = Signal(int)

    def __init__(self, output_dir: str):
        super().__init__()
        self.output_dir = output_dir

    @Slot()
    def run(self):
        try:
            exporter = CSVExporter(SQLITE_DB_PATH)
            # FIX: Passa callback para emitir progresso durante a exportação
            exported_files = exporter.export_all_data(
                self.output_dir,
                progress_callback=lambda percent: self.progress.emit(percent)
            )
            self.finished.emit(exported_files)
        except Exception as e:
            self.error.emit(f"Erro durante a exportação CSV: {e}")
            self.finished.emit([])


# --- Janela Principal ---

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Elite Dangerous Log Tracker (EDLT)")
        self.setGeometry(100, 100, 1000, 750)
        
        self.log_handler = LogSignalHandler()
        self.log_handler.log_record_signal.connect(self.update_log_viewer)
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.INFO)

        self.backend_core = BackendCore(JOURNAL_DIR)
        self.backend_thread: Optional[QThread] = None
        self.backend_worker: Optional[BackendWorker] = None

        self.setup_ui()
        self.connect_signals()
        
        self.update_status("Pronto para configurar e iniciar.")

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Menu Lateral
        self.nav_menu = QListWidget()
        self.nav_menu.setFixedWidth(180)
        self.main_layout.addWidget(self.nav_menu)

        # Conteúdo Empilhado
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        # Adiciona as visualizações
        self.config_view = ConfigView()
        self.control_view = ControlView()
        self.profit_tracker_view = ProfitTrackerView(self.backend_core)
        self.pilot_ranks_view = PilotRanksView(self.backend_core)
        
        self.stacked_widget.addWidget(self.config_view)
        self.stacked_widget.addWidget(self.control_view)
        self.materials_inventory_view = MaterialsInventoryView(self.backend_core)
        self.stacked_widget.addWidget(self.materials_inventory_view)
        self.stacked_widget.addWidget(self.profit_tracker_view)
        self.stacked_widget.addWidget(self.pilot_ranks_view)

        self.nav_menu.addItem("Configuração")
        self.nav_menu.addItem("Controle")
        self.nav_menu.addItem("Inventário de Materiais")
        self.nav_menu.addItem("Rastreamento de Lucro")
        self.nav_menu.addItem("Ranques do Piloto")

        # Log Viewer
        log_layout = QVBoxLayout()
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setMaximumHeight(200)
        log_layout.addWidget(QLabel("Log de Eventos:"))
        log_layout.addWidget(self.log_viewer)
        self.main_layout.addLayout(log_layout)

        # Marca d'água
        self.watermark_label = QLabel("by CMdr. Katzzero")
        self.watermark_label.setStyleSheet("color: rgba(128, 128, 128, 128); font-size: 10px;")
        self.watermark_label.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        log_layout.addWidget(self.watermark_label)

    def connect_signals(self):
        self.nav_menu.currentRowChanged.connect(self.stacked_widget.setCurrentIndex)
        
        # Configuração
        self.config_view.browse_button.clicked.connect(self.browse_journal_path)
        self.config_view.save_config_button.clicked.connect(self.save_config)
        
        # Controle
        self.control_view.start_button.clicked.connect(self.start_backend_worker)
        self.control_view.stop_button.clicked.connect(self.stop_backend_worker)
        self.control_view.export_button.clicked.connect(self.start_csv_export_worker)

        # Conecta o botão de atualização da nova view
        self.materials_inventory_view.update_button.clicked.connect(self.materials_inventory_view.update_materials_display)

    @Slot()
    def browse_journal_path(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Selecione o Diretório de Logs do Elite Dangerous", JOURNAL_DIR
        )
        if directory:
            self.config_view.journal_path_input.setText(directory)

    @Slot()
    def save_config(self):
        new_journal_dir = self.config_view.journal_path_input.text().strip()
        
        # FIX: Validação do diretório
        if not new_journal_dir:
            QMessageBox.warning(self, "Caminho Vazio", "Por favor, especifique um diretório.")
            return
        
        if not os.path.isdir(new_journal_dir):
            QMessageBox.warning(self, "Diretório Inválido", 
                              "O diretório especificado não existe.")
            return
        
        if not os.access(new_journal_dir, os.R_OK):
            QMessageBox.warning(self, "Sem Permissão", 
                              "Sem permissão de leitura no diretório especificado.")
            return
        
        self.backend_core.JOURNAL_DIR = new_journal_dir
        self.update_status(f"Configurações salvas. Caminho: {new_journal_dir}")
        self.control_view.start_button.setEnabled(True)
        QMessageBox.information(self, "Sucesso", 
                              "Configurações salvas. Você pode iniciar o monitoramento.")

    @Slot(str)
    def update_log_viewer(self, message: str):
        self.log_viewer.append(message)
        # Auto-scroll para o final
        self.log_viewer.verticalScrollBar().setValue(
            self.log_viewer.verticalScrollBar().maximum()
        )

    @Slot(str)
    def update_status(self, message: str):
        self.control_view.status_label.setText(f"Status: {message}")

    @Slot()
    def start_backend_worker(self):
        if self.backend_core.is_running:
            QMessageBox.warning(self, "Aviso", "O monitoramento já está em execução.")
            return

        self.backend_thread = QThread()
        self.backend_worker = BackendWorker(self.backend_core)
        self.backend_worker.moveToThread(self.backend_thread)

        self.backend_thread.started.connect(self.backend_worker.run)
        self.backend_worker.finished.connect(self.backend_thread.quit)
        self.backend_worker.finished.connect(self.backend_worker.deleteLater)
        self.backend_thread.finished.connect(self.backend_thread.deleteLater)
        self.backend_worker.error.connect(self.handle_backend_error)

        self.backend_thread.start()
        self.update_status("Monitoramento Iniciado...")
        self.control_view.start_button.setEnabled(False)
        self.control_view.stop_button.setEnabled(True)

    @Slot()
    def stop_backend_worker(self):
        if self.backend_core.is_running:
            self.backend_core.stop_monitoring()
            if self.backend_thread:
                self.backend_thread.quit()
                self.backend_thread.wait(2000)
            self.update_status("Monitoramento Parado.")
            self.control_view.start_button.setEnabled(True)
            self.control_view.stop_button.setEnabled(False)

    @Slot(str)
    def handle_backend_error(self, error_message: str):
        QMessageBox.critical(self, "Erro no Backend", error_message)
        self.stop_backend_worker()

    @Slot()
    def start_csv_export_worker(self):
        output_dir = QFileDialog.getExistingDirectory(
            self, "Selecione o Diretório para Exportar CSV"
        )
        if not output_dir:
            return

        self.update_status("Exportando CSV...")
        self.control_view.progress_bar.setVisible(True)
        # FIX: Modo determinado (0-100%) ao invés de indeterminado
        self.control_view.progress_bar.setRange(0, 100)
        self.control_view.progress_bar.setValue(0)
        
        export_thread = QThread()
        export_worker = CSVExportWorker(output_dir)
        export_worker.moveToThread(export_thread)

        export_thread.started.connect(export_worker.run)
        export_worker.finished.connect(export_thread.quit)
        export_worker.finished.connect(export_worker.deleteLater)
        export_thread.finished.connect(export_thread.deleteLater)
        export_worker.finished.connect(self.handle_export_finished)
        export_worker.error.connect(self.handle_export_error)
        # FIX: Conectar o sinal de progresso à barra
        export_worker.progress.connect(self.control_view.progress_bar.setValue)

        export_thread.start()

    @Slot(list)
    def handle_export_finished(self, exported_files: list):
        self.control_view.progress_bar.setVisible(False)
        self.update_status("Exportação CSV Concluída.")
        
        if exported_files:
            QMessageBox.information(
                self, "Exportação Concluída", 
                f"Exportados {len(exported_files)} arquivos com sucesso!"
            )
        else:
            QMessageBox.warning(
                self, "Exportação Incompleta", 
                "Nenhum arquivo foi exportado. Verifique os logs."
            )

    @Slot(str)
    def handle_export_error(self, error_msg: str):
        self.control_view.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Erro de Exportação", error_msg)
        self.update_status("Erro na exportação CSV.")

    def closeEvent(self, event):
        self.stop_backend_worker()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
