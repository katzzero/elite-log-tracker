# Instalação - Elite Dangerous Log Tracker

## Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## Instalação das Dependências

### Método 1: Instalação Automática (Recomendado)

**Windows:**
```batch
install.bat
```

**Linux/Mac:**
```bash
chmod +x install.sh
./install.sh
```

### Método 2: Instalação Manual

```bash
pip install -r requirements.txt
```

Ou instale individualmente:

```bash
pip install PySide6 watchdog
```

## Verificação das Dependências

Antes de executar o aplicativo, você pode verificar se todas as dependências estão instaladas:

```bash
python check_dependencies.py
```

## Iniciando o Aplicativo

Após instalar as dependências:

```bash
python app.py
```

## Solução de Problemas

### Erro: "No module named 'watchdog'" ou "No module named 'PySide6'"

Isso indica que as dependências não foram instaladas. Execute:

```bash
pip install -r requirements.txt
```

### Erro: "pip não é reconhecido"

Certifique-se de que Python foi adicionado ao PATH durante a instalação. Tente:

```bash
python -m pip install -r requirements.txt
```

### Permissão negada no Linux/Mac

Use `pip3` e `python3`:

```bash
pip3 install -r requirements.txt
python3 app.py
```

Ou instale em modo usuário:

```bash
pip install --user -r requirements.txt
```
