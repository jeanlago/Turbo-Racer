import os

# Tela
LARGURA, ALTURA = 1024, 768
FPS = 60

# Caminhos de projeto/asset
DIR_BASE = os.path.dirname(__file__)
DIR_PROJETO = os.path.abspath(os.path.join(DIR_BASE, ".."))
DIR_SPRITES = os.path.join(DIR_PROJETO, "assets", "images", "car_sprites")
CAMINHO_MAPA = os.path.join(DIR_PROJETO, "assets", "images", "maps", "Map_1.png")

# Cores/HSV da pista
CORES_PISTA = [(31, 23, 38), (0, 0, 0), (240, 224, 0), (144, 105, 0)]
TOLERANCIA_COR = 18

# Parâmetros HSV para detectar “asfalto”
HSV_S_MAX = 45   # pouca saturação
HSV_V_MAX = 55   # escuro
