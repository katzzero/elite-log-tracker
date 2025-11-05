# Elite Dangerous Log Tracker (EDLT)

## 🇧🇷 Português

### Visão Geral
O **Elite Dangerous Log Tracker (EDLT)** é um software cross-platform (Windows/Linux) com interface gráfica (GUI) desenvolvido em Python e PySide6 (Qt) para monitorar em tempo real os logs de diário (Journal files) do jogo Elite Dangerous e integrar dados de APIs externas (como EDDN). 

O objetivo principal é persistir todos os dados coletados em um banco de dados **MySQL** e permitir a exportação para arquivos **CSV**, mantendo uma separação lógica entre dados do **Piloto** e dados do **Universo**.

#### Principais Funcionalidades
*   **Monitoramento em Tempo Real:** Lê o arquivo de diário do Elite Dangerous à medida que novos eventos são registrados, garantindo a sincronização em tempo real.
*   **Persistência em MySQL:** Armazena os dados em dois bancos de dados separados (`db_piloto` e `db_universo`) para organização e análise.
*   **Integração com API (EDDN):** Preparado para receber dados do Elite Dangerous Data Network (EDDN) para informações de mercado e universo (Nota: A integração real com EDDN requer bibliotecas ZeroMQ e é um placeholder no código devido à complexidade de ambiente).
*   **Interface Gráfica (GUI):** Permite configurar as credenciais do MySQL e o caminho dos logs de forma intuitiva.
*   **Exportação CSV:** Exporta o conteúdo de todas as tabelas relevantes para arquivos CSV com um clique.

### Pré-requisitos

Para rodar o EDLT, você precisará dos seguintes componentes instalados e configurados:

1.  **Python 3.x:** A linguagem de programação principal.
2.  **MySQL Server:** O banco de dados para persistência dos dados.
3.  **Elite Dangerous:** O jogo deve estar instalado e ter gerado pelo menos um arquivo de log de diário.

### Instalação e Configuração

#### 1. Configuração do MySQL

Você deve criar os bancos de dados e tabelas usando o esquema fornecido.

1.  **Acesse o console do MySQL** (ou utilize uma ferramenta como DBeaver, MySQL Workbench, etc.).
2.  **Crie o usuário e senha** que serão usados pelo aplicativo. No código, o padrão é `ed_user` e `ed_password`.
    ```sql
    -- Exemplo de criação de usuário (ajuste conforme a sua segurança)
    CREATE USER 'ed_user'@'localhost' IDENTIFIED BY 'ed_password';
    GRANT ALL PRIVILEGES ON *.* TO 'ed_user'@'localhost' WITH GRANT OPTION;
    FLUSH PRIVILEGES;
    ```
3.  **Execute o script de esquema SQL** (`mysql_schema.sql`) para criar os bancos de dados (`db_piloto`, `db_universo`) e as tabelas.

    ```sql
    -- Conteúdo do arquivo mysql_schema.sql
    -- Você pode executar o arquivo diretamente no console:
    -- source /caminho/para/mysql_schema.sql
    ```

#### 2. Instalação das Dependências Python

1.  **Navegue até o diretório `elite-log-tracker`** onde o arquivo `requirements.txt` está localizado.
2.  **Instale as dependências** usando `pip`:
    ```bash
    pip install -r requirements.txt
    ```
    Isso instalará `mysql-connector-python`, `watchdog`, `requests` e `PySide6`.

#### 3. Localização dos Logs do Elite Dangerous

O caminho padrão dos logs de diário no Windows é:
`C:\Users\[SeuNomeDeUsuário]\Saved Games\Frontier Developments\Elite Dangerous`

Você precisará desse caminho para configurar o aplicativo na GUI.

### Uso do Aplicativo

1.  **Inicie o aplicativo** executando o script `app.py`:
    ```bash
    python app.py
    ```

2.  **Visualização "Configuração":**
    *   Preencha os campos de **Host, Usuário e Senha** do MySQL (padrão: `localhost`, `ed_user`, `ed_password`).
    *   Use o botão **"Procurar Diretório"** para selecionar o caminho dos logs de diário do Elite Dangerous.
    *   Clique em **"Salvar Configurações e Testar Conexão"**. Uma mensagem de sucesso deve aparecer. Se houver erro, verifique se o MySQL está rodando e se as credenciais estão corretas.

3.  **Visualização "Controle":**
    *   O botão **"Iniciar Monitoramento"** será habilitado após salvar as configurações.
    *   Clique em **"Iniciar Monitoramento"** para começar a ler o arquivo de diário em tempo real.
    *   O **"Log de Eventos"** na parte inferior da janela mostrará as mensagens de sucesso para cada evento de diário processado e inserido no MySQL.

4.  **Exportação CSV:**
    *   Clique em **"Exportar Dados para CSV"**.
    *   Selecione o diretório onde deseja salvar os arquivos.
    *   O aplicativo criará um arquivo CSV para cada tabela.

---
---

## 🇬🇧 English

### Overview
The **Elite Dangerous Log Tracker (EDLT)** is a cross-platform (Windows/Linux) software with a Graphical User Interface (GUI) developed in Python and PySide6 (Qt) to monitor Elite Dangerous Journal files in real-time and integrate data from external APIs (such as EDDN).

The main goal is to persist all collected data into a **MySQL** database and allow export to **CSV** files, maintaining a logical separation between **Pilot** data and **Universe** data.

#### Key Features
*   **Real-Time Monitoring:** Reads the Elite Dangerous Journal file as new events are logged, ensuring real-time synchronization.
*   **MySQL Persistence:** Stores data in two separate databases (`db_piloto` and `db_universo`) for organization and analysis.
*   **API Integration (EDDN):** Prepared to receive data from the Elite Dangerous Data Network (EDDN) for market and universe information (Note: Actual EDDN integration requires ZeroMQ libraries and is a placeholder in the code due to environmental complexity).
*   **Graphical User Interface (GUI):** Allows intuitive configuration of MySQL credentials and the Journal log path.
*   **CSV Export:** Exports the content of all relevant tables to CSV files with a single click.

### Prerequisites

To run EDLT, you will need the following components installed and configured:

1.  **Python 3.x:** The main programming language.
2.  **MySQL Server:** The database for data persistence.
3.  **Elite Dangerous:** The game must be installed and have generated at least one Journal log file.

### Installation and Configuration

#### 1. MySQL Setup

You must create the databases and tables using the provided schema.

1.  **Access the MySQL console** (or use a tool like DBeaver, MySQL Workbench, etc.).
2.  **Create the user and password** that will be used by the application. In the code, the default is `ed_user` and `ed_password`.
    ```sql
    -- Example user creation (adjust according to your security)
    CREATE USER 'ed_user'@'localhost' IDENTIFIED BY 'ed_password';
    GRANT ALL PRIVILEGES ON *.* TO 'ed_user'@'localhost' WITH GRANT OPTION;
    FLUSH PRIVILEGES;
    ```
3.  **Execute the SQL schema script** (`mysql_schema.sql`) to create the databases (`db_piloto`, `db_universo`) and the tables.

    ```sql
    -- Content of the mysql_schema.sql file
    -- You can execute the file directly in the console:
    -- source /path/to/mysql_schema.sql
    ```

#### 2. Python Dependencies Installation

1.  **Navigate to the `elite-log-tracker` directory** where the `requirements.txt` file is located.
2.  **Install the dependencies** using `pip`:
    ```bash
    pip install -r requirements.txt
    ```
    This will install `mysql-connector-python`, `watchdog`, `requests`, and `PySide6`.

#### 3. Elite Dangerous Logs Location

The default path for Journal logs on Windows is:
`C:\Users\[YourUserName]\Saved Games\Frontier Developments\Elite Dangerous`

You will need this path to configure the application in the GUI.

### Application Usage

1.  **Start the application** by running the `app.py` script:
    ```bash
    python app.py
    ```

2.  **"Configuration" View:**
    *   Fill in the **Host, User, and Password** fields for MySQL (default: `localhost`, `ed_user`, `ed_password`).
    *   Use the **"Browse Directory"** button to select the path to the Elite Dangerous Journal logs.
    *   Click **"Save Settings and Test Connection"**. A success message should appear. If there is an error, check if MySQL is running and if the credentials are correct.

3.  **"Control" View:**
    *   The **"Start Monitoring"** button will be enabled after saving the settings.
    *   Click **"Start Monitoring"** to begin reading the Journal file in real-time.
    *   The **"Event Log"** at the bottom of the window will show success messages for each Journal event processed and inserted into MySQL.

4.  **CSV Export:**
    *   Click **"Export Data to CSV"**.
    *   Select the directory where you want to save the files.
    *   The application will create a CSV file for each table.

## Project Structure

```
elite-log-tracker/
├── README.md               # This file.
├── requirements.txt        # Python dependencies.
├── mysql_schema.sql        # Script for creating MySQL tables.
├── app.py                  # Graphical User Interface (PySide6).
├── main.py                 # Backend Core (Log Monitoring and MySQL Persistence).
├── eddn_client.py          # Logic for EDDN API integration (Placeholder).
└── csv_exporter.py         # Logic for exporting data to CSV.
```
