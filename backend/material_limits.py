# Dicionário de Limites de Capacidade de Materiais de Engenharia
# Fonte: Elite Dangerous Wiki (Fandom) - https://elite-dangerous.fandom.com/wiki/Materials

MATERIAL_CAPACITY = {
    # Grade 1 (Very Common) - Limite: 300
    1: 300,
    # Grade 2 (Common) - Limite: 250
    2: 250,
    # Grade 3 (Standard) - Limite: 200
    3: 200,
    # Grade 4 (Rare) - Limite: 150
    4: 150,
    # Grade 5 (Very Rare) - Limite: 100
    5: 100,
}

# Dicionário de Categorias de Materiais
# Usado para agrupar na visualização
MATERIAL_CATEGORIES = {
    'Raw': ['Carbon', 'Phosphorus', 'Sulphur', 'Iron', 'Nickel', 'Rhenium', 'Lead', 'Vanadium', 'Chromium', 'Molybdenum', 'Zinc', 'Germanium', 'Arsenic', 'Zirconium', 'Niobium', 'Technetium', 'Cadmium', 'Tin', 'Tungsten', 'Mercury', 'Boron', 'Yttrium', 'Ruthenium', 'Selenium', 'Tellurium', 'Polonium', 'Antimony'],
    'Manufactured': ['Chemical Storage Units', 'Chemical Processors', 'Chemical Distillery', 'Chemical Manipulators', 'Pharmaceutical Isolators', 'Tempered Alloys', 'Heat Resistant Ceramics', 'Precipitated Alloys', 'Thermic Alloys', 'Military Grade Alloys', 'Heat Conduction Wiring', 'Heat Dispersion Plate', 'Heat Exchangers', 'Heat Vanes', 'Proto Heat Radiators', 'Basic Conductors', 'Conductive Components', 'Conductive Ceramics', 'Conductive Polymers', 'Biotech Conductors', 'Mechanical Scrap', 'Mechanical Equipment', 'Mechanical Components', 'Configurable Components', 'Improvised Components', 'Grid Resistors', 'Hybrid Capacitors', 'Electrochemical Arrays', 'Polymer Capacitors', 'Military Supercapacitors', 'Worn Shield Emitters', 'Shield Emitters', 'Shielding Sensors', 'Compound Shielding', 'Imperial Shielding', 'Compact Composites', 'Filament Composites', 'High Density Composites', 'Proprietary Composites', 'Core Dynamics Composites', 'Crystal Shards', 'Flawed Focus Crystals', 'Focus Crystals', 'Refined Focus Crystals', 'Exquisite Focus Crystals', 'Salvaged Alloys', 'Galvanising Alloys', 'Phase Alloys', 'Proto Light Alloys', 'Proto Radiolic Alloys', 'Meta-Alloys'],
    'Encoded': ['Exceptional Scrambled Emission Data', 'Irregular Emission Data', 'Unexpected Emission Data', 'Decoded Emission Data', 'Abnormal Compact Emissions Data', 'Atypical Disrupted Wake Echoes', 'Anomalous FSD Telemetry', 'Strange Wake Solutions', 'Eccentric Hyperspace Trajectories', 'Datamined Wake Exceptions', 'Distorted Shield Cycle Recordings', 'Inconsistent Shield Soak Analysis', 'Untypical Shield Scans', 'Aberrant Shield Pattern Analysis', 'Peculiar Shield Frequency Data', 'Unusual Encrypted Files', 'Tagged Encryption Codes', 'Open Symmetric Keys', 'Atypical Encryption Archives', 'Adaptive Encryptors Capture', 'Anomalous Bulk Scan Data', 'Unidentified Scan Archives', 'Classified Scan Databanks', 'Divergent Scan Data', 'Classified Scan Fragment', 'Specialised Legacy Firmware', 'Modified Consumer Firmware', 'Cracked Industrial Firmware', 'Security Firmware Patch', 'Modified Embedded Firmware']
}

# Mapeamento reverso para obter a categoria e o grau de um material (para uso no backend)
MATERIAL_GRADE_MAP = {}
for category, materials in MATERIAL_CATEGORIES.items():
    # A ordem na Wiki é por linha, mas o grau é implícito pela coluna.
    # Como o Journal fornece o nome exato, vamos mapear o nome para o grau.
    # O Journal (e o EDDiscovery) não fornece o 'Grade' diretamente, apenas a quantidade.
    # O mapeamento do nome para o grau é complexo e propenso a erros.
    # A abordagem mais segura é: O evento 'Materials' ou 'MaterialInventory' lista os materiais e suas quantidades.
    # O limite de capacidade é determinado pelo *nome* do material, que está associado a um *grau*.
    # Vamos usar uma lista de todos os materiais e seus graus (obtida de fontes externas) para o backend.
    # Por enquanto, o backend só precisa do nome e da quantidade. A GUI fará o cálculo do limite.
    pass

# Para a GUI, vamos precisar de um dicionário que mapeie o nome do material para o seu grau (1 a 5)
# Isso é necessário para obter o limite de capacidade de MATERIAL_CAPACITY.
# Como a lista da Wiki é grande e não está em formato fácil de parsear, vou incluir um dicionário auxiliar.
# Exemplo de material e seu grau (baseado na estrutura da Wiki):
MATERIAL_TO_GRADE = {
    'Carbon': 1, 'Vanadium': 2, 'Niobium': 3, 'Yttrium': 4,
    'Phosphorus': 1, 'Chromium': 2, 'Molybdenum': 3, 'Technetium': 4,
    'Sulphur': 1, 'Manganese': 2, 'Cadmium': 3, 'Ruthenium': 4,
    'Iron': 1, 'Zinc': 2, 'Tin': 3, 'Selenium': 4,
    'Nickel': 1, 'Germanium': 2, 'Tungsten': 3, 'Tellurium': 4,
    'Rhenium': 1, 'Arsenic': 2, 'Mercury': 3, 'Polonium': 4,
    'Lead': 1, 'Zirconium': 2, 'Boron': 3, 'Antimony': 4,
    
    # Manufactured - G1 a G5
    'Chemical Storage Units': 1, 'Chemical Processors': 2, 'Chemical Distillery': 3, 'Chemical Manipulators': 4, 'Pharmaceutical Isolators': 5,
    'Tempered Alloys': 1, 'Heat Resistant Ceramics': 2, 'Precipitated Alloys': 3, 'Thermic Alloys': 4, 'Military Grade Alloys': 5,
    'Heat Conduction Wiring': 1, 'Heat Dispersion Plate': 2, 'Heat Exchangers': 3, 'Heat Vanes': 4, 'Proto Heat Radiators': 5,
    'Basic Conductors': 1, 'Conductive Components': 2, 'Conductive Ceramics': 3, 'Conductive Polymers': 4, 'Biotech Conductors': 5,
    'Mechanical Scrap': 1, 'Mechanical Equipment': 2, 'Mechanical Components': 3, 'Configurable Components': 4, 'Improvised Components': 5,
    'Grid Resistors': 1, 'Hybrid Capacitors': 2, 'Electrochemical Arrays': 3, 'Polymer Capacitors': 4, 'Military Supercapacitors': 5,
    'Worn Shield Emitters': 1, 'Shield Emitters': 2, 'Shielding Sensors': 3, 'Compound Shielding': 4, 'Imperial Shielding': 5,
    'Compact Composites': 1, 'Filament Composites': 2, 'High Density Composites': 3, 'Proprietary Composites': 4, 'Core Dynamics Composites': 5,
    'Crystal Shards': 1, 'Flawed Focus Crystals': 2, 'Focus Crystals': 3, 'Refined Focus Crystals': 4, 'Exquisite Focus Crystals': 5,
    'Salvaged Alloys': 1, 'Galvanising Alloys': 2, 'Phase Alloys': 3, 'Proto Light Alloys': 4, 'Proto Radiolic Alloys': 5,
    'Meta-Alloys': 5, # Meta-Alloys é um caso especial, G5.

    # Encoded - G1 a G5
    'Exceptional Scrambled Emission Data': 1, 'Irregular Emission Data': 2, 'Unexpected Emission Data': 3, 'Decoded Emission Data': 4, 'Abnormal Compact Emissions Data': 5,
    'Atypical Disrupted Wake Echoes': 1, 'Anomalous FSD Telemetry': 2, 'Strange Wake Solutions': 3, 'Eccentric Hyperspace Trajectories': 4, 'Datamined Wake Exceptions': 5,
    'Distorted Shield Cycle Recordings': 1, 'Inconsistent Shield Soak Analysis': 2, 'Untypical Shield Scans': 3, 'Aberrant Shield Pattern Analysis': 4, 'Peculiar Shield Frequency Data': 5,
    'Unusual Encrypted Files': 1, 'Tagged Encryption Codes': 2, 'Open Symmetric Keys': 3, 'Atypical Encryption Archives': 4, 'Adaptive Encryptors Capture': 5,
    'Anomalous Bulk Scan Data': 1, 'Unidentified Scan Archives': 2, 'Classified Scan Databanks': 3, 'Divergent Scan Data': 4, 'Classified Scan Fragment': 5,
    'Specialised Legacy Firmware': 1, 'Modified Consumer Firmware': 2, 'Cracked Industrial Firmware': 3, 'Security Firmware Patch': 4, 'Modified Embedded Firmware': 5
}
