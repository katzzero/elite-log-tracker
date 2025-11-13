"""
Dados de ranques do Elite Dangerous.
Fonte: Elite Dangerous Journal Documentation e Elite Dangerous Wiki
"""

from typing import Dict, List

# Dicionário de mapeamento de ranques (índice para nome)
# Os índices são os valores que vêm no evento "Rank" do Journal.
RANK_NAMES: Dict[str, List[str]] = {
    "Combat": [
        "Harmless", "Mostly Harmless", "Novice", "Competent", 
        "Expert", "Master", "Dangerous", "Deadly", "Elite"
    ],
    "Trade": [
        "Penniless", "Mostly Penniless", "Dealer", "Merchant", 
        "Broker", "Entrepreneur", "Tycoon", "Elite", 
        "Elite I", "Elite II", "Elite III", "Elite IV", "Elite V"
    ],
    "Explore": [
        "Aimless", "Mostly Aimless", "Scout", "Surveyor", 
        "Trailblazer", "Pathfinder", "Pioneer", "Elite", 
        "Elite I", "Elite II", "Elite III", "Elite IV", "Elite V"
    ],
    "CQC": [
        "Helpless", "Mostly Helpless", "Amateur", "Semi-Pro", 
        "Professional", "Champion", "Hero", "Legend", "Elite"
    ],
    "Federation": [
        "None", "Recruit", "Cadet", "Midshipman", "Petty Officer", 
        "Chief Petty Officer", "Warrant Officer", "Ensign", "Lieutenant", 
        "Lt. Commander", "Post Commander", "Post Captain", "Rear Admiral", 
        "Vice Admiral", "Admiral"
    ],
    "Empire": [
        "None", "Outsider", "Serf", "Master", "Squire", "Knight", 
        "Lord", "Baron", "Viscount", "Count", "Earl", "Marquis", 
        "Duke", "Prince", "King"
    ],
}

# FIX: Corrigido typo - era PILOTS__FEDERATION_RANKS (dois underscores)
# Ranques da Pilots Federation que usam progresso de 0 a 100%
# O evento "Progress" só é enviado para estes ranques
PILOTS_FEDERATION_RANKS: List[str] = ["Combat", "Trade", "Explore", "CQC"]

# Ranques de Superpotência (Federation e Empire)
# Também usam sistema de progresso mas com diferentes mecânicas
SUPERPOWER_RANKS: List[str] = ["Federation", "Empire"]

# Mapeamento de índice para tipo de ranque
RANK_TYPES: Dict[int, str] = {
    0: "Combat",
    1: "Trade",
    2: "Explore",
    3: "Federation",
    4: "Empire",
    5: "CQC",
}

# Ranques que possuem o sistema de Elite V (Trade e Explore)
ELITE_V_RANKS: List[str] = ["Trade", "Explore"]

# Nomes dos ranques Elite estendidos
ELITE_V_RANKS_NAMES: List[str] = ["Elite I", "Elite II", "Elite III", "Elite IV", "Elite V"]

# Índices dos ranques Elite estendidos nas listas de ranques
ELITE_V_RANKS_INDEX: List[int] = [8, 9, 10, 11, 12]


def get_rank_name(rank_type: str, rank_value: int) -> str:
    """
    Retorna o nome do ranque baseado no tipo e valor.
    
    Args:
        rank_type: Tipo do ranque (Combat, Trade, etc.)
        rank_value: Índice do ranque (0-based)
        
    Returns:
        Nome do ranque ou "Unknown" se inválido
        
    Example:
        >>> get_rank_name("Combat", 5)
        'Master'
    """
    if rank_type not in RANK_NAMES:
        return "Unknown"
    
    ranks = RANK_NAMES[rank_type]
    if 0 <= rank_value < len(ranks):
        return ranks[rank_value]
    
    return "Unknown"


def get_max_rank_value(rank_type: str) -> int:
    """
    Retorna o valor máximo de ranque para um tipo específico.
    
    Args:
        rank_type: Tipo do ranque (Combat, Trade, etc.)
        
    Returns:
        Valor máximo (índice) ou -1 se tipo inválido
        
    Example:
        >>> get_max_rank_value("Combat")
        8  # Elite é o índice 8
    """
    if rank_type not in RANK_NAMES:
        return -1
    
    return len(RANK_NAMES[rank_type]) - 1


def is_max_rank(rank_type: str, rank_value: int) -> bool:
    """
    Verifica se o piloto atingiu o ranque máximo.
    
    Args:
        rank_type: Tipo do ranque
        rank_value: Valor atual do ranque
        
    Returns:
        True se é ranque máximo, False caso contrário
        
    Example:
        >>> is_max_rank("Combat", 8)
        True  # Elite
    """
    return rank_value == get_max_rank_value(rank_type)


def get_next_rank_name(rank_type: str, current_rank: int) -> str:
    """
    Retorna o nome do próximo ranque.
    
    Args:
        rank_type: Tipo do ranque
        current_rank: Ranque atual
        
    Returns:
        Nome do próximo ranque ou "Maximum" se já está no máximo
        
    Example:
        >>> get_next_rank_name("Combat", 5)
        'Dangerous'
    """
    if is_max_rank(rank_type, current_rank):
        return "Maximum"
    
    return get_rank_name(rank_type, current_rank + 1)


def validate_rank_data(rank_type: str, rank_value: int, progress: float) -> bool:
    """
    Valida se os dados de ranque estão consistentes.
    
    Args:
        rank_type: Tipo do ranque
        rank_value: Valor do ranque (índice)
        progress: Progresso para o próximo ranque (0.0 a 1.0)
        
    Returns:
        True se dados válidos, False caso contrário
    """
    # Verifica se o tipo de ranque existe
    if rank_type not in RANK_NAMES:
        return False
    
    # Verifica se o valor está dentro do range
    if rank_value < 0 or rank_value > get_max_rank_value(rank_type):
        return False
    
    # Verifica se o progresso está dentro do range
    if progress < 0.0 or progress > 1.0:
        return False
    
    # Se está no ranque máximo, progresso deve ser 0 ou 1
    if is_max_rank(rank_type, rank_value) and progress > 0.0:
        return False
    
    return True


# Constantes de compatibilidade com código antigo
# FIX: Mantido para retrocompatibilidade mas deprecated
# TODO: Remover em versão futura
PILOTS__FEDERATION_RANKS = PILOTS_FEDERATION_RANKS  # Deprecated: Use PILOTS_FEDERATION_RANKS
