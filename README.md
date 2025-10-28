# Elite Dangerous Data Collector (EDDC)

## Visão Geral
O **Elite Dangerous Data Collector (EDDC)** é um software cross-platform (Windows/Linux) com interface gráfica (GUI) desenvolvido em Python e PySide6 (Qt) para monitorar em tempo real os logs de diário (Journal files) do jogo Elite Dangerous e integrar dados de APIs externas (como EDDN). 

O objetivo principal é persistir todos os dados coletados em um banco de dados **MySQL** e permitir a exportação para arquivos **CSV**, mantendo uma separação lógica entre dados do **Piloto** e dados do **Universo**.

### Principais Funcionalidades
*   **Monitoramento em Tempo Real:** Lê o arquivo de diário do Elite Dangerous à medida que novos eventos são registrados, garantindo a sincronização em tempo real.
*   **Persistência em MySQL:** Armazena os dados em dois bancos de dados separados (`db_piloto` e `db_universo`) para organização e análise.
*   **Integração com API (EDDN):** Preparado para receber dados do Elite Dangerous Data Network (EDDN) para informações de mercado e universo (Nota: A integração real com EDDN requer bibliotecas ZeroMQ e é um placeholder no código devido à complexidade de ambiente).
*   **Interface Gráfica (GUI):** Permite configurar as credenciais do MySQL e o caminho dos logs de forma intuitiva.
*   **Exportação CSV:** Exporta o conteúdo de todas as tabelas relevantes para arquivos CSV com um clique.

## Pré-requisitos

Para rodar o EDDC, você precisará dos seguintes componentes instalados e configurados:

1.  **Python 3.x:** A linguagem de programação principal.
2.  **MySQL Server:** O banco de dados para persistência dos dados.
3.  **Elite Dangerous:** O jogo deve estar instalado e ter gerado pelo menos um arquivo de log de diário.

## Instalação e Configuração

### 1. Configuração do MySQL

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
    
    -- db_piloto (Dados do Piloto): journal_events, pilot_journeys, pilot_transactions
    -- db_universo (Dados do Universo): star_systems, stations, commodity_prices
    ```

### 2. Instalação das Dependências Python

1.  **Navegue até o diretório `ed_data_collector`** onde o arquivo `requirements.txt` está localizado.
2.  **Instale as dependências** usando `pip`:
    ```bash
    pip install -r requirements.txt
    ```
    Isso instalará `mysql-connector-python`, `watchdog`, `requests` e `PySide6`.

### 3. Localização dos Logs do Elite Dangerous

O caminho padrão dos logs de diário no Windows é:
`C:\Users\[SeuNomeDeUsuário]\Saved Games\Frontier Developments\Elite Dangerous`

Você precisará desse caminho para configurar o aplicativo na GUI.

## Uso do Aplicativo

1.  **Inicie o aplicativo** executando o script `run_app.py`:
    ```bash
    python run_app.py
    ```

2.  **Aba "Configuração":**
    *   Preencha os campos de **Host, Usuário e Senha** do MySQL (padrão: `localhost`, `ed_user`, `ed_password`).
    *   Use o botão **"Procurar Diretório"** para selecionar o caminho dos logs de diário do Elite Dangerous.
    *   Clique em **"Salvar Configurações e Testar Conexão"**. Uma mensagem de sucesso deve aparecer. Se houver erro, verifique se o MySQL está rodando e se as credenciais estão corretas.

3.  **Aba "Controle e Status":**
    *   O botão **"Iniciar Monitoramento"** será habilitado após salvar as configurações.
    *   Clique em **"Iniciar Monitoramento"** para começar a ler o arquivo de diário em tempo real.
    *   O **"Log de Eventos"** na parte inferior da janela mostrará as mensagens de sucesso para cada evento de diário processado e inserido no MySQL.

4.  **Exportação CSV:**
    *   Clique em **"Exportar Dados para CSV"**.
    *   Selecione o diretório onde deseja salvar os arquivos.
    *   O aplicativo criará um arquivo CSV para cada tabela (`db_piloto_journal_events.csv`, `db_universo_star_systems.csv`, etc.).

## Estrutura do Projeto

```
ed_data_collector/
├── README.md               # Este arquivo.
├── requirements.txt        # Dependências Python.
├── mysql_schema.sql        # Script para criação das tabelas MySQL.
├── run_app.py              # Script principal para iniciar a GUI.
├── backend/
│   ├── __init__.py
│   ├── main.py             # Core do Backend (Monitoramento de Logs e Persistência MySQL).
│   ├── eddn_client.py      # Lógica de integração com a API EDDN (Placeholder).
│   └── csv_exporter.py     # Lógica para exportação de dados para CSV.
└── gui/
    └── app.py              # Interface Gráfica (PySide6).
```
