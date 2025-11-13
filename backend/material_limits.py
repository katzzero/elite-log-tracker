"""
Dados de limites de capacidade de materiais de engenharia do Elite Dangerous.
Fonte: Elite Dangerous Wiki - https://elite-dangerous.fandom.com/wiki/Materials
"""

from typing import Dict, List, Optional, Tuple

# Limites de capacidade por grau de material
MATERIAL_CAPACITY: Dict[int, int] = {
    1: 300,  # Grade 1 (Very Common)
    2: 250,  # Grade 2 (Common)
    3: 200,  # Grade 3 (Standard)
    4: 150,  # Grade 4 (Rare)
    5: 100,  # Grade 5 (Very Rare)
}

# Categorias de materiais (para agrupamento na visualização)
MATERIAL_CATEGORIES: Dict[str, List[str]] = {
    'Raw': [
        'Carbon', 'Phosphorus', 'Sulphur', 'Iron', 'Nickel', 'Rhenium', 'Lead', 
        'Vanadium', 'Chromium', 'Molybdenum', 'Zinc', 'Germanium', 'Arsenic', 
        'Zirconium', 'Niobium', 'Technetium', 'Cadmium', 'Tin', 'Tungsten', 
        'Mercury', 'Boron', 'Yttrium', 'Ruthenium', 'Selenium', 'Tellurium', 
        'Polonium', 'Antimony'
    ],
    'Manufactured': [
        'Chemical Storage Units', 'Chemical Processors', 'Chemical Distillery', 
        'Chemical Manipulators', 'Pharmaceutical Isolators', 'Tempered Alloys', 
        'Heat Resistant Ceramics', 'Precipitated Alloys', 'Thermic Alloys', 
        'Military Grade Alloys', 'Heat Conduction Wiring', 'Heat Dispersion Plate', 
        'Heat Exchangers', 'Heat Vanes', 'Proto Heat Radiators', 'Basic Conductors', 
        'Conductive Components', 'Conductive Ceramics', 'Conductive Polymers', 
        'Biotech Conductors', 'Mechanical Scrap', 'Mechanical Equipment', 
        'Mechanical Components', 'Configurable Components', 'Improvised Components', 
        'Grid Resistors', 'Hybrid Capacitors', 'Electrochemical Arrays', 
        'Polymer Capacitors', 'Military Supercapacitors', 'Worn Shield Emitters', 
        'Shield Emitters', 'Shielding Sensors', 'Compound Shielding', 
        'Imperial Shielding', 'Compact Composites', 'Filament Composites', 
        'High Density Composites', 'Proprietary Composites', 'Core Dynamics Composites', 
        'Crystal Shards', 'Flawed Focus Crystals', 'Focus Crystals', 
        'Refined Focus Crystals', 'Exquisite Focus Crystals', 'Salvaged Alloys', 
        'Galvanising Alloys', 'Phase Alloys', 'Proto Light Alloys', 
        'Proto Radiolic Alloys', 'Meta-Alloys'
    ],
    'Encoded': [
        'Exceptional Scrambled Emission Data', 'Irregular Emission Data', 
        'Unexpected Emission Data', 'Decoded Emission Data', 
        'Abnormal Compact Emissions Data', 'Atypical Disrupted Wake Echoes', 
        'Anomalous FSD Telemetry', 'Strange Wake Solutions', 
        'Eccentric Hyperspace Trajectories', 'Datamined Wake Exceptions', 
        'Distorted Shield Cycle Recordings', 'Inconsistent Shield Soak Analysis', 
        'Untypical Shield Scans', 'Aberrant Shield Pattern Analysis', 
        'Peculiar Shield Frequency Data', 'Unusual Encrypted Files', 
        'Tagged Encryption Codes', 'Open Symmetric Keys', 
        'Atypical Encryption Archives', 'Adaptive Encryptors Capture', 
        'Anomalous Bulk Scan Data', 'Unidentified Scan Archives', 
        'Classified Scan Databanks', 'Divergent Scan Data', 
        'Classified Scan Fragment', 'Specialised Legacy Firmware', 
        'Modified Consumer Firmware', 'Cracked Industrial Firmware', 
        'Security Firmware Patch', 'Modified Embedded Firmware'
    ]
}

# Mapeamento de material para grau (1-5)
MATERIAL_TO_GRADE: Dict[str, int] = {
    # Raw Materials - Grade 1 to 4 (7 elementos por grau)
    'Carbon': 1, 'Vanadium': 2, 'Niobium': 3, 'Yttrium': 4,
    'Phosphorus': 1, 'Chromium': 2, 'Molybdenum': 3, 'Technetium': 4,
    'Sulphur': 1, 'Manganese': 2, 'Cadmium': 3, 'Ruthenium': 4,
    'Iron': 1, 'Zinc': 2, 'Tin': 3, 'Selenium': 4,
    'Nickel': 1, 'Germanium': 2, 'Tungsten': 3, 'Tellurium': 4,
    'Rhenium': 1, 'Arsenic': 2, 'Mercury': 3, 'Polonium': 4,
    'Lead': 1, 'Zirconium': 2, 'Boron': 3, 'Antimony': 4,
    
    # Manufactured Materials - Grade 1 to 5 (por categoria)
    'Chemical Storage Units': 1, 'Chemical Processors': 2, 'Chemical Distillery': 3, 
    'Chemical Manipulators': 4, 'Pharmaceutical Isolators': 5,
    
    'Tempered Alloys': 1, 'Heat Resistant Ceramics': 2, 'Precipitated Alloys': 3, 
    'Thermic Alloys': 4, 'Military Grade Alloys': 5,
    
    'Heat Conduction Wiring': 1, 'Heat Dispersion Plate': 2, 'Heat Exchangers': 3, 
    'Heat Vanes': 4, 'Proto Heat Radiators': 5,
    
    'Basic Conductors': 1, 'Conductive Components': 2, 'Conductive Ceramics': 3, 
    'Conductive Polymers': 4, 'Biotech Conductors': 5,
    
    'Mechanical Scrap': 1, 'Mechanical Equipment': 2, 'Mechanical Components': 3, 
    'Configurable Components': 4, 'Improvised Components': 5,
    
    'Grid Resistors': 1, 'Hybrid Capacitors': 2, 'Electrochemical Arrays': 3, 
    'Polymer Capacitors': 4, 'Military Supercapacitors': 5,
    
    'Worn Shield Emitters': 1, 'Shield Emitters': 2, 'Shielding Sensors': 3, 
    'Compound Shielding': 4, 'Imperial Shielding': 5,
    
    'Compact Composites': 1, 'Filament Composites': 2, 'High Density Composites': 3, 
    'Proprietary Composites': 4, 'Core Dynamics Composites': 5,
    
    'Crystal Shards': 1, 'Flawed Focus Crystals': 2, 'Focus Crystals': 3, 
    'Refined Focus Crystals': 4, 'Exquisite Focus Crystals': 5,
    
    'Salvaged Alloys': 1, 'Galvanising Alloys': 2, 'Phase Alloys': 3, 
    'Proto Light Alloys': 4, 'Proto Radiolic Alloys': 5,
    
    'Meta-Alloys': 5,  # Caso especial
    
    # Encoded Materials - Grade 1 to 5
    'Exceptional Scrambled Emission Data': 1, 'Irregular Emission Data': 2, 
    'Unexpected Emission Data': 3, 'Decoded Emission Data': 4, 
    'Abnormal Compact Emissions Data': 5,
    
    'Atypical Disrupted Wake Echoes': 1, 'Anomalous FSD Telemetry': 2, 
    'Strange Wake Solutions': 3, 'Eccentric Hyperspace Trajectories': 4, 
    'Datamined Wake Exceptions': 5,
    
    'Distorted Shield Cycle Recordings': 1, 'Inconsistent Shield Soak Analysis': 2, 
    'Untypical Shield Scans': 3, 'Aberrant Shield Pattern Analysis': 4, 
    'Peculiar Shield Frequency Data': 5,
    
    'Unusual Encrypted Files': 1, 'Tagged Encryption Codes': 2, 
    'Open Symmetric Keys': 3, 'Atypical Encryption Archives': 4, 
    'Adaptive Encryptors Capture': 5,
    
    'Anomalous Bulk Scan Data': 1, 'Unidentified Scan Archives': 2, 
    'Classified Scan Databanks': 3, 'Divergent Scan Data': 4, 
    'Classified Scan Fragment': 5,
    
    'Specialised Legacy Firmware': 1, 'Modified Consumer Firmware': 2, 
    'Cracked Industrial Firmware': 3, 'Security Firmware Patch': 4, 
    'Modified Embedded Firmware': 5
}

# FIX: Criar mapeamento reverso (categoria do material)
MATERIAL_TO_CATEGORY: Dict[str, str] = {}
for category, materials in MATERIAL_CATEGORIES.items():
    for material in materials:
        MATERIAL_TO_CATEGORY[material] = category


def get_material_grade(material_name: str) -> Optional[int]:
    """
    Retorna o grau (1-5) de um material.
    
    Args:
        material_name: Nome do material
        
    Returns:
        Grau do material (1-5) ou None se não encontrado
        
    Example:
        >>> get_material_grade("Carbon")
        1
        >>> get_material_grade("Pharmaceutical Isolators")
        5
    """
    return MATERIAL_TO_GRADE.get(material_name)


def get_material_capacity(material_name: str) -> Optional[int]:
    """
    Retorna o limite de capacidade de um material.
    
    Args:
        material_name: Nome do material
        
    Returns:
        Capacidade máxima ou None se material não encontrado
        
    Example:
        >>> get_material_capacity("Carbon")
        300  # Grade 1
        >>> get_material_capacity("Pharmaceutical Isolators")
        100  # Grade 5
    """
    grade = get_material_grade(material_name)
    if grade is None:
        return None
    
    return MATERIAL_CAPACITY.get(grade)


def get_material_category(material_name: str) -> Optional[str]:
    """
    Retorna a categoria de um material (Raw, Manufactured, Encoded).
    
    Args:
        material_name: Nome do material
        
    Returns:
        Categoria do material ou None se não encontrado
        
    Example:
        >>> get_material_category("Carbon")
        'Raw'
        >>> get_material_category("Chemical Storage Units")
        'Manufactured'
    """
    return MATERIAL_TO_CATEGORY.get(material_name)


def get_material_info(material_name: str) -> Optional[Dict[str, any]]:
    """
    Retorna informações completas sobre um material.
    
    Args:
        material_name: Nome do material
        
    Returns:
        Dicionário com grade, category e capacity, ou None se não encontrado
        
    Example:
        >>> get_material_info("Carbon")
        {'grade': 1, 'category': 'Raw', 'capacity': 300}
    """
    grade = get_material_grade(material_name)
    if grade is None:
        return None
    
    return {
        'grade': grade,
        'category': get_material_category(material_name),
        'capacity': MATERIAL_CAPACITY[grade]
    }


def is_material_at_capacity(material_name: str, current_count: int) -> bool:
    """
    Verifica se um material atingiu sua capacidade máxima.
    
    Args:
        material_name: Nome do material
        current_count: Quantidade atual
        
    Returns:
        True se está no limite, False caso contrário
        
    Example:
        >>> is_material_at_capacity("Carbon", 300)
        True
        >>> is_material_at_capacity("Carbon", 250)
        False
    """
    capacity = get_material_capacity(material_name)
    if capacity is None:
        return False
    
    return current_count >= capacity


def get_material_fill_percentage(material_name: str, current_count: int) -> Optional[float]:
    """
    Retorna a porcentagem de preenchimento de um material.
    
    Args:
        material_name: Nome do material
        current_count: Quantidade atual
        
    Returns:
        Porcentagem (0.0 a 1.0) ou None se material não encontrado
        
    Example:
        >>> get_material_fill_percentage("Carbon", 150)
        0.5  # 50%
    """
    capacity = get_material_capacity(material_name)
    if capacity is None or capacity == 0:
        return None
    
    return min(current_count / capacity, 1.0)


def validate_material_count(material_name: str, count: int) -> Tuple[bool, Optional[str]]:
    """
    Valida se a quantidade de um material é válida.
    
    Args:
        material_name: Nome do material
        count: Quantidade a validar
        
    Returns:
        Tupla (válido, mensagem_de_erro)
        
    Example:
        >>> validate_material_count("Carbon", 150)
        (True, None)
        >>> validate_material_count("Carbon", 350)
        (False, "Count exceeds capacity of 300")
    """
    if count < 0:
        return False, "Count cannot be negative"
    
    capacity = get_material_capacity(material_name)
    if capacity is None:
        return False, f"Unknown material: {material_name}"
    
    if count > capacity:
        return False, f"Count exceeds capacity of {capacity}"
    
    return True, None


def get_all_materials_by_category(category: str) -> List[str]:
    """
    Retorna lista de todos os materiais de uma categoria.
    
    Args:
        category: Categoria (Raw, Manufactured, Encoded)
        
    Returns:
        Lista de nomes de materiais ou lista vazia se categoria inválida
        
    Example:
        >>> materials = get_all_materials_by_category("Raw")
        >>> len(materials)
        27
    """
    return MATERIAL_CATEGORIES.get(category, [])


def get_all_materials_by_grade(grade: int) -> List[str]:
    """
    Retorna lista de todos os materiais de um grau específico.
    
    Args:
        grade: Grau do material (1-5)
        
    Returns:
        Lista de nomes de materiais
        
    Example:
        >>> materials = get_all_materials_by_grade(5)
        >>> "Pharmaceutical Isolators" in materials
        True
    """
    return [
        material for material, mat_grade in MATERIAL_TO_GRADE.items()
        if mat_grade == grade
    ]


# Constantes de compatibilidade
MATERIAL_LIMITS = MATERIAL_CAPACITY  # Alias para retrocompatibilidade
