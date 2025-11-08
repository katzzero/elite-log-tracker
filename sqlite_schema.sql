-- Novo esquema SQLite consolidado para Elite Dangerous Log Tracker (EDLT)

-- Tabela principal para armazenar o histórico de eventos do Journal
-- O campo 'event_hash' é usado para prevenir a inserção de eventos duplicados
CREATE TABLE IF NOT EXISTS journal_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_data TEXT NOT NULL, -- JSON string do evento original
    event_hash TEXT UNIQUE NOT NULL -- Hash do timestamp + event_type + parte do event_data para unicidade
);

-- Tabela consolidada para o status atual do piloto (substitui pilot_status, pilot_ranks, pilot_materials)
-- Esta tabela armazena o estado mais recente e é atualizada a cada evento relevante.
CREATE TABLE IF NOT EXISTS pilot_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pilot_name TEXT UNIQUE NOT NULL, -- O nome do piloto é a chave única
    last_update TEXT NOT NULL,
    
    -- Status da Nave
    ship_id INTEGER,
    ship_name TEXT,
    ship_model TEXT,
    system_name TEXT,
    station_name TEXT,
    
    -- Ranques (valores numéricos e progresso)
    rank_combat INTEGER DEFAULT 0,
    progress_combat REAL DEFAULT 0.0,
    rank_trade INTEGER DEFAULT 0,
    progress_trade REAL DEFAULT 0.0,
    rank_explore INTEGER DEFAULT 0,
    progress_explore REAL DEFAULT 0.0,
    rank_cqc INTEGER DEFAULT 0,
    progress_cqc REAL DEFAULT 0.0,
    rank_federation INTEGER DEFAULT 0,
    progress_federation REAL DEFAULT 0.0,
    rank_empire INTEGER DEFAULT 0,
    progress_empire REAL DEFAULT 0.0
);

-- Tabela para o inventário de materiais (substitui pilot_materials)
-- Armazena o inventário atualizado pelo evento 'Materials'
CREATE TABLE IF NOT EXISTS pilot_materials (
    material_name TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    count INTEGER NOT NULL
);

-- Tabela para o rastreamento de lucro (substitui pilot_profit)
CREATE TABLE IF NOT EXISTS pilot_profit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    profit_type TEXT NOT NULL, -- TRADE, BOUNTY, EXPLORATION, EXOBIOLOGY, CARTOGRAPHY
    amount INTEGER NOT NULL
);

-- Tabela para os módulos da nave (substitui ship_modules)
-- Armazena o loadout atual da nave
CREATE TABLE IF NOT EXISTS ship_modules (
    ship_id INTEGER NOT NULL,
    slot TEXT NOT NULL,
    module TEXT NOT NULL,
    health REAL NOT NULL,
    PRIMARY KEY (ship_id, slot)
);

-- Tabela para os corpos celestes e estações (substitui system_bodies e stations)
-- Armazena dados do sistema atual
CREATE TABLE IF NOT EXISTS system_data (
    name TEXT PRIMARY KEY, -- Nome do corpo, estação ou sinal
    system_name TEXT NOT NULL,
    type TEXT NOT NULL, -- STAR, PLANET, STATION, SIGNAL
    distance_ls REAL,
    data_json TEXT -- JSON com dados detalhados (ex: terraformable, type of station)
);
