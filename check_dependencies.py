#!/usr/bin/env python3
"""
Elite Dangerous Log Tracker - Dependency Checker
Verifica se todas as dependências necessárias estão instaladas antes de iniciar o aplicativo.
"""

import sys
import subprocess


def check_dependencies():
    """Verifica se todas as dependências estão instaladas."""
    required_modules = {
        'PySide6': 'PySide6',
        'watchdog': 'watchdog',
    }

    missing_modules = []

    for display_name, import_name in required_modules.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_modules.append(display_name)

    return missing_modules


def show_console_error(missing_modules):
    """Exibe erro no console quando dependências estão faltando."""
    print("=" * 70)
    print("ERRO: Dependências não encontradas")
    print("=" * 70)
    print("\nOs seguintes módulos Python são necessários mas não estão instalados:\n")

    for module in missing_modules:
        print(f"  - {module}")

    print("\n" + "-" * 70)
    print("Para instalar todas as dependências, execute:")
    print("\n  pip install " + " ".join(missing_modules))
    print("\nOu use o arquivo requirements.txt:")
    print("\n  pip install -r requirements.txt")
    print("=" * 70)


def show_gui_error(missing_modules):
    """Exibe erro em janela gráfica quando dependências estão faltando."""
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox

        app = QApplication(sys.argv)

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Elite Dangerous Log Tracker - Erro de Dependências")
        msg.setText("Dependências não encontradas")

        details = "Os seguintes módulos Python são necessários:\n\n"
        details += "\n".join([f"  • {module}" for module in missing_modules])
        details += "\n\nPara instalar, execute no terminal:\n\n"
        details += f"pip install {' '.join(missing_modules)}"

        msg.setInformativeText(details)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    except ImportError:
        # Se PySide6 não está disponível, usa console
        show_console_error(missing_modules)


def install_dependencies_prompt():
    """Pergunta ao usuário se deseja instalar as dependências automaticamente."""
    print("\nDeseja tentar instalar as dependências automaticamente? (s/n): ", end="")
    response = input().strip().lower()

    if response in ['s', 'sim', 'y', 'yes']:
        return True
    return False


def auto_install_dependencies(missing_modules):
    """Tenta instalar as dependências automaticamente."""
    print("\nInstalando dependências...")

    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install"
        ] + missing_modules)

        print("\n✓ Dependências instaladas com sucesso!")
        print("\nReinicie o aplicativo para continuar.")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\n✗ Erro ao instalar dependências: {e}")
        print("\nPor favor, instale manualmente usando:")
        print(f"  pip install {' '.join(missing_modules)}")
        return False


if __name__ == "__main__":
    missing = check_dependencies()

    if missing:
        # Verifica se PySide6 está entre os módulos faltantes
        if 'PySide6' in missing:
            show_console_error(missing)

            # Oferece instalação automática em modo console
            if install_dependencies_prompt():
                if auto_install_dependencies(missing):
                    sys.exit(0)
            sys.exit(1)
        else:
            # PySide6 disponível, pode usar GUI
            show_gui_error(missing)
            sys.exit(1)

    print("✓ Todas as dependências estão instaladas.")
    print("Iniciando Elite Dangerous Log Tracker...\n")
