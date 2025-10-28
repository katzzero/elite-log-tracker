import sys
import os

# Adiciona o diretório da GUI ao path para garantir que o app.py seja encontrado
sys.path.append(os.path.join(os.path.dirname(__file__), 'gui'))

# Define a variável de ambiente para que o PySide6 funcione corretamente no Linux/X11
# Útil para ambientes sem display manager completo.
# os.environ['QT_QPA_PLATFORM'] = 'offscreen' # Não usar offscreen se for mostrar GUI
# os.environ['QT_LOGGING_RULES'] = 'qt.qpa.*=false' # Opcional: silenciar logs do Qt

try:
    from gui.app import MainWindow, QApplication
except ImportError as e:
    print(f"Erro ao importar módulos da GUI: {e}")
    print("Certifique-se de que o PySide6 está instalado corretamente.")
    sys.exit(1)

if __name__ == '__main__':
    # Cria a aplicação Qt
    app = QApplication(sys.argv)
    
    # Cria e mostra a janela principal
    window = MainWindow()
    window.show()
    
    # Inicia o loop de eventos da aplicação
    sys.exit(app.exec())

