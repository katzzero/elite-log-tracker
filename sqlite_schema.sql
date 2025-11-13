-- Novo esquema SQLite consolidado para Elite Dangerous Log Tracker (EDLT)

-- Tabela principal para armazenar o histórico de eventos do Journal
-- O campo 'event_hash' é usado para prevenir a inserção de eventos duplicados
CREATE TABLE IF NOT EXISTS journal_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_data TEXT NOT NULL, -- JSON string do evento original
    event_hash TEXT UNIQUE NOT NULL -- Hash do timestamp + event_type + event_data completo para unicidade
);

-- FIX: Índices para melhorar performance de queries
CREATE INDEX IF NOT EXISTS idx_journal_timestamp ON journal_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_journal_event_type ON journal_events(event_type);
CREATE INDEX IF NOT EXISTS idx_journal_hash ON journal_events(event_hash);

-- Tabela consolidada para o status atual do piloto
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
    progress_combat REAL DEFAULT 0.0 CHECK(progress_combat >= 0.0 AND progress_combat <= 1.0),
    rank_trade INTEGER DEFAULT 0,
    progress_trade REAL DEFAULT 0.0 CHECK(progress_trade >= 0.0 AND progress_trade <= 1.0),
    rank_explore INTEGER DEFAULT 0,
    progress_explore REAL DEFAULT 0.0 CHECK(progress_explore >= 0.0 AND progress_explore <= 1.0),
    rank_cqc INTEGER DEFAULT 0,
    progress_cqc REAL DEFAULT 0.0 CHECK(progress_cqc >= 0.0 AND progress_cqc <= 1.0),
    rank_federation INTEGER DEFAULT 0,
    progress_federation REAL DEFAULT 0.0 CHECK(progress_federation >= 0.0 AND progress_federation <= 1.0),
    rank_empire INTEGER DEFAULT 0,
    progress_empire REAL DEFAULT 0.0 CHECK(progress_empire >= 0.0 AND progress_empire <= 1.0)
);

-- FIX: Índice para pilot_status
CREATE INDEX IF NOT EXISTS idx_pilot_name ON pilot_status(pilot_name);

-- Tabela para o inventário de materiais
-- Armazena o inventário atualizado pelo evento 'Materials'
CREATE TABLE IF NOT EXISTS pilot_materials (
    material_name TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    count INTEGER NOT NULL CHECK(count >= 0)
);

-- FIX: Índice para categoria de materiais
CREATE INDEX IF NOT EXISTS idx_material_category ON pilot_materials(category);

-- Tabela para o rastreamento de lucro
CREATE TABLE IF NOT EXISTS pilot_profit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    profit_type TEXT NOT NULL, -- TRADE, BOUNTY, EXPLORATION, EXOBIOLOGY, CARTOGRAPHY
    amount INTEGER NOT NULL
);

-- FIX: Índices para otimizar queries de lucro
CREATE INDEX IF NOT EXISTS idx_profit_type ON pilot_profit(profit_type);
CREATE INDEX IF NOT EXISTS idx_profit_timestamp ON pilot_profit(timestamp);
CREATE INDEX IF NOT EXISTS idx_profit_type_timestamp ON pilot_profit(profit_type, timestamp);

-- Tabela para os módulos da nave
-- Armazena o loadout atual da nave
CREATE TABLE IF NOT EXISTS ship_modules (
    ship_id INTEGER NOT NULL,
    slot TEXT NOT NULL,
    module TEXT NOT NULL,
    health REAL NOT NULL CHECK(health >= 0.0 AND health <= 1.0),
    PRIMARY KEY (ship_id, slot)
);

-- FIX: Índice para ship_modules
CREATE INDEX IF NOT EXISTS idx_ship_modules_ship_id ON ship_modules(ship_id);

-- Tabela para os corpos celestes e estações
-- Armazena dados do sistema atual
CREATE TABLE IF NOT EXISTS system_data (
    name TEXT PRIMARY KEY, -- Nome do corpo, estação ou sinal
    system_name TEXT NOT NULL,
    type TEXT NOT NULL, -- STAR, PLANET, STATION, SIGNAL
    distance_ls REAL,
    data_json TEXT -- JSON com dados detalhados (ex: terraformable, type of station)
);

-- FIX: Índices para system_data
CREATE INDEX IF NOT EXISTS idx_system_name ON system_data(system_name);
CREATE INDEX IF NOT EXISTS idx_system_type ON system_data(type);
CREATE INDEX IF NOT EXISTS idx_system_name_type ON system_data(system_name, type);
