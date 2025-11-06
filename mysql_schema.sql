-- Esquema SQL para o Coletor de Dados Elite Dangerous
-- O usuário solicitou a separação de dados do piloto e do universo.

-- 1. Banco de Dados do Piloto (db_piloto)

CREATE DATABASE IF NOT EXISTS db_piloto;
USE db_piloto;

-- Tabela para armazenar todos os eventos do diário (Journal)
-- O campo Event_JSON guarda o JSON completo do evento para flexibilidade
CREATE TABLE IF NOT EXISTS journal_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    commander_name VARCHAR(100),
    event_json JSON NOT NULL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Viagens (simplificada a partir de FSDJump, Docked, Undocked)
CREATE TABLE IF NOT EXISTS pilot_journeys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    system_name VARCHAR(255) NOT NULL,
    star_class VARCHAR(50),
    distance_from_sol DOUBLE,
    jump_distance DOUBLE,
    is_docked BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id) REFERENCES journal_events(id) -- Opcional: linkar ao evento original
);

-- Tabela de Inventário de Materiais (obtido via evento Materials)
CREATE TABLE IF NOT EXISTS pilot_materials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    material_name VARCHAR(100) NOT NULL,
    material_category VARCHAR(50) NOT NULL,
    count INT NOT NULL,
    UNIQUE KEY unique_material (material_name)
);

-- Tabela de Ranques do Piloto (obtido via evento Rank)
CREATE TABLE IF NOT EXISTS pilot_ranks (
    rank_type VARCHAR(50) PRIMARY KEY, -- Ex: Combat, Trade, Explore, Federation, Empire, CQC
    rank_value INT NOT NULL, -- O valor numérico do ranque (0 a 8 ou 0 a 14)
    rank_progress DOUBLE NOT NULL, -- O progresso para o próximo ranque (0.0 a 1.0)
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabela de Transações (simplificada a partir de Buy/Sell/Market events)
CREATE TABLE IF NOT EXISTS pilot_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    station_name VARCHAR(255) NOT NULL,
    commodity_name VARCHAR(255) NOT NULL,
    transaction_type ENUM('BUY', 'SELL', 'MINING', 'MISSION_REWARD') NOT NULL,
    price INT,
    quantity INT,
    total_cost INT
);

-- 2. Banco de Dados do Universo (db_universo)

CREATE DATABASE IF NOT EXISTS db_universo;
USE db_universo;

-- Tabela de Sistemas Estelares (obtidos via EDDN ou Journal)
CREATE TABLE IF NOT EXISTS star_systems (
    id INT AUTO_INCREMENT PRIMARY KEY,
    system_name VARCHAR(255) UNIQUE NOT NULL,
    system_address BIGINT UNIQUE,
    x DOUBLE,
    y DOUBLE,
    z DOUBLE,
    allegiance VARCHAR(100),
    government VARCHAR(100),
    population BIGINT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabela de Estações (obtidos via EDDN ou Journal)
CREATE TABLE IF NOT EXISTS stations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    station_name VARCHAR(255) NOT NULL,
    system_name VARCHAR(255) NOT NULL,
    station_type VARCHAR(100),
    distance_from_star INT,
    market_id BIGINT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (system_name) REFERENCES star_systems(system_name)
);

-- Tabela de Preços de Commodities (obtidos via EDDN)
CREATE TABLE IF NOT EXISTS commodity_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    station_name VARCHAR(255) NOT NULL,
    commodity_name VARCHAR(255) NOT NULL,
    supply INT,
    demand INT,
    buy_price INT,
    sell_price INT,
    FOREIGN KEY (station_name) REFERENCES stations(station_name)
);
