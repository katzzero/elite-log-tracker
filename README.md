# Elite Dangerous Log Tracker (EDLT)

## 🇧🇷 Português

### Visão Geral
O **Elite Dangerous Log Tracker (EDLT)** é um software cross-platform (Windows/Linux) com interface gráfica (GUI) desenvolvido em Python e PySide6 (Qt) para monitorar em tempo real os logs de diário (Journal files) do jogo Elite Dangerous.

O objetivo principal é persistir todos os dados coletados em um banco de dados **SQLite** local, que é mais seguro e não requer configuração externa, e permitir a exportação para arquivos **CSV**. O novo esquema de banco de dados foi consolidado para melhorar a segurança e a integridade dos dados.

#### Principais Funcionalidades
*   **Monitoramento em Tempo Real:** Lê o arquivo de diário do Elite Dangerous à medida que novos eventos são registrados, garantindo a sincronização em tempo real.
*   **Persistência em SQLite:** Armazena os dados em um único arquivo de banco de dados SQLite (`edlt.db`), eliminando a necessidade de um servidor MySQL e melhorando a segurança.
*   **Visualização de Status:** Exibe o status atual do piloto (localização, nave, módulos).
*   **Visualização de Ranques:** Exibe o ranque atual e o progresso percentual para o próximo ranque em todas as categorias.
*   **Rastreamento de Lucro:** Exibe o lucro total por categoria (Comércio, Recompensa, Exploração, Exobiologia, Cartografia), formatado em Cr, MCr e BCr.
*   **Inventário de Materiais:** Exibe o inventário de materiais de engenharia com barras de progresso para o limite máximo.
*   **Exportação CSV:** Exporta o conteúdo de todas as tabelas relevantes para arquivos CSV com um clique.

### Pré-requisitos

Para rodar o EDLT, você precisará dos seguintes componentes instalados e configurados:

1.  **Python 3.x:** A linguagem de programação principal.
2.  **Elite Dangerous:** O jogo deve estar instalado e ter gerado pelo menos um arquivo de log de diário.

### Instalação e Configuração

#### 1. Instalação das Dependências Python

1.  **Navegue até o diretório `elite-log-tracker`** onde o arquivo `requirements.txt` está localizado.
2.  **Instale as dependências** usando `pip`:
    ```bash
    pip install -r requirements.txt
    ```
    Isso instalará `watchdog`, `requests` e `PySide6`. **O conector MySQL não é mais necessário.**

#### 2. Localização dos Logs do Elite Dangerous

O caminho padrão dos logs de diário no Windows é:
`C:\Users\[SeuNomeDeUsuário]\Saved Games\Frontier Developments\Elite Dangerous`

Você precisará desse caminho para configurar o aplicativo na GUI.

### Uso do Aplicativo

1.  **Inicie o aplicativo** executando o script `app.py`:
    ```bash
    python app.py
    ```

2.  **Visualização "Configuração":**
    *   Use o botão **"Procurar Diretório"** para selecionar o caminho dos logs de diário do Elite Dangerous.
    *   Clique em **"Salvar Configurações"**. O banco de dados SQLite (`edlt.db`) será criado automaticamente no diretório do aplicativo.

3.  **Visualização "Controle":**
    *   Clique em **"Iniciar Monitoramento"** para começar a ler o arquivo de diário em tempo real.
    *   O **"Log de Eventos"** na parte inferior da janela mostrará as mensagens de sucesso para cada evento de diário processado e inserido no SQLite.

4.  **Exportação CSV:**
    *   Clique em **"Exportar Dados para CSV"**.
    *   Selecione o diretório onde deseja salvar os arquivos.

---
---

## 🇬🇧 English

### Overview
The **Elite Dangerous Log Tracker (EDLT)** is a cross-platform (Windows/Linux) software with a Graphical User Interface (GUI) developed in Python and PySide6 (Qt) to monitor Elite Dangerous Journal files in real-time.

The main goal is to persist all collected data into a local **SQLite** database, which is more secure and requires no external configuration, and allow export to **CSV** files. The new database schema has been consolidated to improve security and data integrity.

#### Key Features
*   **Real-Time Monitoring:** Reads the Elite Dangerous Journal file as new events are logged, ensuring real-time synchronization.
*   **SQLite Persistence:** Stores data in a single SQLite database file (`edlt.db`), eliminating the need for a MySQL server and enhancing security.
*   **Status Visualization:** Displays the current pilot status (location, ship, modules).
*   **Ranks Visualization:** Displays the current rank and percentage progress to the next rank in all categories.
*   **Profit Tracking:** Displays the total profit by category (Trade, Bounty, Exploration, Exobiology, Cartography), formatted in Cr, MCr, and BCr.
*   **Materials Inventory:** Displays the engineering materials inventory with progress bars to the maximum limit.
*   **CSV Export:** Exports the content of all relevant tables to CSV files with a single click.

### Prerequisites

To run EDLT, you will need the following components installed and configured:

1.  **Python 3.x:** The main programming language.
2.  **Elite Dangerous:** The game must be installed and have generated at least one Journal log file.

### Installation and Configuration

#### 1. Python Dependencies Installation

1.  **Navigate to the `elite-log-tracker` directory** where the `requirements.txt` file is located.
2.  **Install the dependencies** using `pip`:
    ```bash
    pip install -r requirements.txt
    ```
    This will install `watchdog`, `requests`, and `PySide6`. **The MySQL connector is no longer required.**

#### 2. Elite Dangerous Logs Location

The default path for Journal logs on Windows is:
`C:\Users\[YourUserName]\Saved Games\Frontier Developments\Elite Dangerous`

You will need this path to configure the application in the GUI.

### Application Usage

1.  **Start the application** by running the `app.py` script:
    ```bash
    python app.py
    ```

2.  **"Configuration" View:**
    *   Use the **"Browse Directory"** button to select the path to the Elite Dangerous Journal logs.
    *   Click **"Save Settings"**. The SQLite database (`edlt.db`) will be automatically created in the application directory.

3.  **"Control" View:**
    *   Click **"Start Monitoring"** to begin reading the Journal file in real-time.
    *   The **"Event Log"** at the bottom of the window will show success messages for each Journal event processed and inserted into SQLite.

4.  **CSV Export:**
    *   Click **"Export Data to CSV"**.
    *   Select the directory where you want to save the files.

## Project Structure

```
elite-log-tracker/
├── README.md               # This file.
├── requirements.txt        # Python dependencies.
├── sqlite_schema.sql       # Script for creating SQLite tables.
├── app.py                  # Graphical User Interface (PySide6).
├── main.py                 # Backend Core (Log Monitoring and SQLite Persistence).
├── eddn_client.py          # Logic for EDDN API integration (Placeholder).
├── csv_exporter.py         # Logic for exporting data to CSV.
└── backend/
    ├── material_limits.py  # Data for material capacity limits.
    └── rank_data.py        # Data for rank names and progression.
```
