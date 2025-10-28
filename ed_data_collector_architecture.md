# Arquitetura do Coletor de Dados Elite Dangerous

## Objetivo
Desenvolver um software cross-platform (Linux/Windows) com interface gráfica (GUI) para coletar dados em tempo real do jogo Elite Dangerous, utilizando os logs de diário (Journal files) e APIs de terceiros (como EDDN e Inara), e armazenar os dados em um banco de dados MySQL e arquivos CSV, separando informações do piloto e do universo.

## Fontes de Dados

| Fonte | Tipo de Dado | Formato | Acesso |
| :--- | :--- | :--- | :--- |
| **Journal Files (Frontier)** | Dados do Piloto (Viagens, Comércio, Missões, Inventário) | JSONL (JSON Lines) | Leitura em tempo real do arquivo local. |
| **EDDN (Elite Dangerous Data Network)** | Dados do Universo (Preços de Comodidades, Status de Estações) | JSON (via API/Webhook) | Consumo da API ou monitoramento de *streams*. |
| **Inara API** | Dados do Piloto (Status, Reputação, Frotas) | JSON (via API) | Requisições HTTP para sincronização de dados. |

## Separação de Dados (MySQL)

Para atender ao requisito de separação, o banco de dados MySQL será estruturado em duas áreas lógicas, possivelmente em *databases* ou *schemas* separados, ou através de prefixos de tabelas distintos.

1.  **`db_piloto` (Dados do Piloto)**
    *   Eventos de Diário (Journal Events): `FSDJump`, `Docked`, `SellCommodity`, `Loadout`, etc.
    *   Tabelas: `viagens`, `transacoes`, `inventario`, `status_piloto`.

2.  **`db_universo` (Dados do Universo)**
    *   Dados de Estações e Sistemas (obtidos via EDDN).
    *   Tabelas: `sistemas`, `estacoes`, `precos_commodities`.

## Arquitetura do Software (Python + Qt/Tkinter)

O software será desenvolvido em Python para garantir a portabilidade e facilidade de integração com bibliotecas de manipulação de dados e MySQL.

### 1. Backend (Python)
*   **Monitoramento de Logs:** Utilizar `tail -f` (via subprocesso ou biblioteca Python) para monitorar o arquivo de diário mais recente em tempo real.
*   **Processamento de Eventos:** Analisar cada linha JSON do log, identificar o tipo de evento e rotear o dado para a função de persistência apropriada.
*   **Integração com MySQL:** Utilizar a biblioteca `mysql-connector-python` ou `SQLAlchemy` para gerenciar a conexão e a inserção de dados nas tabelas `db_piloto` e `db_universo`.
*   **Integração com API:** Módulo `requests` para interagir com APIs como Inara e EDDN.

### 2. Frontend (GUI Cross-Platform)
*   **Tecnologia:** Recomenda-se **PyQt** ou **PySide** (bindings de Qt para Python) para criar uma interface gráfica rica e verdadeiramente cross-platform (Windows, Linux, macOS).
*   **Funcionalidades:**
    *   Configuração da localização dos Journal Files e credenciais do MySQL.
    *   Visualização em tempo real dos eventos sendo processados.
    *   Botão para forçar a sincronização com APIs externas.
    *   Função de exportação de dados para CSV.

## Fases de Desenvolvimento

1.  **Pesquisa e Planejamento** (Concluído)
2.  **Estrutura do Banco de Dados** (Próxima Fase)
3.  **Desenvolvimento do Backend** (Monitoramento de Logs e MySQL)
4.  **Integração com APIs e Exportação CSV**
5.  **Desenvolvimento da GUI**
6.  **Testes e Documentação**
7.  **Entrega**

## Próxima Etapa
Definir o esquema SQL para as tabelas `viagens` (piloto) e `sistemas` (universo) como ponto de partida.
