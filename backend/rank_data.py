# Dicionário de mapeamento de ranques (índice para nome)
# Os índices são os valores que vêm no evento "Rank" do Journal.
# Fonte: Elite Dangerous Journal Documentation e Elite Dangerous Wiki

RANK_NAMES = {
    "Combat": ["Harmless", "Mostly Harmless", "Novice", "Competent", "Expert", "Master", "Dangerous", "Deadly", "Elite"],
    "Trade": ["Penniless", "Mostly Penniless", "Dealer", "Merchant", "Broker", "Entrepreneur", "Tycoon", "Elite", "Elite I", "Elite II", "Elite III", "Elite IV", "Elite V"],
    "Explore": ["Aimless", "Mostly Aimless", "Scout", "Surveyor", "Trailblazer", "Pathfinder", "Pioneer", "Elite", "Elite I", "Elite II", "Elite III", "Elite IV", "Elite V"],
    "CQC": ["Helpless", "Mostly Helpless", "Amateur", "Semi-Pro", "Professional", "Champion", "Hero", "Legend", "Elite"],
    "Federation": ["None", "Recruit", "Cadet", "Midshipman", "Petty Officer", "Chief Petty Officer", "Warrant Officer", "Ensign", "Lieutenant", "Lt. Commander", "Post Commander", "Post Captain", "Rear Admiral", "Vice Admiral", "Admiral"],
    "Empire": ["None", "Outsider", "Serf", "Master", "Squire", "Knight", "Lord", "Baron", "Viscount", "Count", "Earl", "Marquis", "Duke", "Prince", "King"],
}

# Ranques que usam o sistema de progresso de 0 a 100% (Progress event)
# O evento "Progress" só é enviado para os ranques da Pilots Federation (Combat, Trade, Explore, CQC)
PILOTS__FEDERATION_RANKS = ["Combat", "Trade", "Explore", "CQC"]

# Ranques que usam o sistema de progresso de 0 a 100% (Progress event)
# O evento "Progress" só é enviado para os ranques da Pilots Federation (Combat, Trade, Explore, CQC)
SUPERPOWER_RANKS = ["Federation", "Empire"]

# Mapeamento de índice para nome para facilitar a exibição
RANK_TYPES = {
    0: "Combat",
    1: "Trade",
    2: "Explore",
    3: "Federation",
    4: "Empire",
    5: "CQC",
}

# Ranques que possuem o sistema de Elite V (Trade e Explore)
ELITE_V_RANKS = ["Trade", "Explore"]

# Ranques que possuem o sistema de Elite V (Trade e Explore)
ELITE_V_RANKS_NAMES = ["Elite I", "Elite II", "Elite III", "Elite IV", "Elite V"]

# Ranques que possuem o sistema de Elite V (Trade e Explore)
ELITE_V_RANKS_INDEX = [8, 9, 10, 11, 12]

# Ranques que possuem o sistema de Elite V (Trade e Explore)
ELITE_V_RANKS_PROGRESS = 1000000000 # Valor fictício, pois o progresso para Elite V não é reportado no Journal
