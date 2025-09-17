import os

# ---------- Tela ----------
LARGURA, ALTURA = 1280, 720
FPS = 60

# ---------- Caminhos ----------
DIR_BASE = os.path.dirname(__file__)
DIR_PROJETO = os.path.abspath(os.path.join(DIR_BASE, ".."))
DIR_SPRITES = os.path.join(DIR_PROJETO, "assets", "images", "cars")
DIR_CAR_SELECTION = os.path.join(DIR_PROJETO, "assets", "images", "car_selection")
DIR_MAPS = os.path.join(DIR_PROJETO, "assets", "images", "maps")
DIR_MAPS_GUIDES = os.path.join(DIR_MAPS, "guides")
CAMINHO_MENU = os.path.join(DIR_PROJETO, "assets", "images", "ui", "Menu.png")
CAMINHO_OFICINA = os.path.join(DIR_PROJETO, "assets", "images", "ui", "oficina.png")

# ---------- Sistema de Mapas ----------
MAPAS_DISPONIVEIS = {
    "Map_1": {
        "nome": "Pista Principal",
        "arquivo_mapa": os.path.join(DIR_MAPS, "Map_1.png"),
        "arquivo_guias": os.path.join(DIR_MAPS_GUIDES, "Map_1_guides.png"),
        "arquivo_checkpoints": os.path.join(DIR_MAPS_GUIDES, "Map_1_checkpoints.json"),
        "waypoints_fallback": [
            (820, 140), (930, 360), (860, 620),
            (520, 650), (200, 600), (160, 420),
            (260, 150), (500, 120)
        ]
    }
    # Adicione novos mapas aqui conforme necessário
    # "Map_2": {
    #     "nome": "Pista Secundária",
    #     "arquivo_mapa": os.path.join(DIR_MAPS, "Map_2.png"),
    #     "arquivo_guias": os.path.join(DIR_MAPS_GUIDES, "Map_2_guides.png"),
    #     "arquivo_checkpoints": os.path.join(DIR_MAPS_GUIDES, "Map_2_checkpoints.json"),
    #     "waypoints_fallback": [(100, 100), (200, 200), (300, 300)]
    # }
}

# Mapa atual (pode ser alterado dinamicamente)
MAPA_ATUAL = "Map_1"

# Funções para obter caminhos do mapa atual
def obter_caminho_mapa():
    return MAPAS_DISPONIVEIS[MAPA_ATUAL]["arquivo_mapa"]

def obter_caminho_guias():
    return MAPAS_DISPONIVEIS[MAPA_ATUAL]["arquivo_guias"]

def obter_caminho_checkpoints():
    return MAPAS_DISPONIVEIS[MAPA_ATUAL]["arquivo_checkpoints"]

def obter_waypoints_fallback():
    return MAPAS_DISPONIVEIS[MAPA_ATUAL]["waypoints_fallback"]

# Compatibilidade com código existente
CAMINHO_MAPA = obter_caminho_mapa()
CAMINHO_GUIAS = obter_caminho_guias()
CAMINHO_WAYPOINTS_JSON = obter_caminho_checkpoints()

# ---------- Pista (cores aceitas) / HSV ----------
CORES_PISTA = [(31, 23, 38), (0, 0, 0), (240, 224, 0), (144, 105, 0)]
TOLERANCIA_COR = 18
HSV_S_MAX = 45
HSV_V_MAX = 55

# ---------- Corrida ----------
VOLTAS_OBJETIVO = 3
LINHA_LARGADA = (498, 93, 28, 130)
PONTOS_DE_CONTROLE = [(160, 520, 40, 120), (880, 630, 40, 120), (900, 180, 40, 120)]

# ---------- Controles extras ----------
TURBO_P1 = "K_LSHIFT"
TURBO_P2 = "K_RCTRL"

# ---------- HUD ----------
COR_TEXTO = (255, 255, 255)
COR_SOMBRA = (0, 0, 0)

# ---------- IA / Modo de jogo ----------
USAR_IA_NO_CARRO_2 = False

TRILHAS_IA = [
    {"cor": (255, 170, 60), "tol": 40},   # laranja #FFAA3C
]

# ---------- Checkpoints magenta no guides (opcional) ----------
CHECKPOINT_COR = (255, 0, 255)   # #FF00FF
CHECKPOINT_TOL = 50
CHECKPOINT_MIN_PIXELS = 60

# ---------- Waypoints fallback ----------
WAYPOINTS_MAP_1 = [
    (820, 140), (930, 360), (860, 620),
    (520, 650), (200, 600), (160, 420),
    (260, 150), (500, 120)
]

# ---------- Pure Pursuit ----------
PP_WHEELBASE = 36.0
PP_LD_MIN = 60.0
PP_LD_MAX = 200.0
PP_LD_KV  = 1.5

PP_V_MIN = 50.0   # Reduzido de 70.0 para 50.0
PP_V_MAX = 200.0  # Reduzido de 280.0 para 200.0
PP_K_CURV_SPEED = 120.0  # Reduzido de 180.0 para 120.0

PP_BRAKE_EPS = 25.0
PP_ACCEL_GAIN = 1.2
PP_BRAKE_GAIN = 1.0
PP_STEER_GAIN = 1.0
PP_STEER_DEADZONE = 0.08  # rad (~4.5°)

PP_STUCK_EPS_V = 8.0
PP_STUCK_TIME  = 0.7
PP_RECOVER_TIME = 0.6
PP_RECOVER_STEER_DEG = 28

# ---------- Efeitos / Partículas ----------
DIR_EFFECTS = os.path.join(DIR_PROJETO, "assets", "images", "effects")
CAMINHO_FUMACA = os.path.join(DIR_EFFECTS, "smoke.png")  # coloque seu asset aqui

# ---------- Modo Drift / Pontuação ----------
MODO_DRIFT = True
DRIFT_MIN_VEL = 1.6
DRIFT_PONTOS_BASE = 1.0
DRIFT_PONTOS_VEL_FACTOR = 0.06
DRIFT_DECAY_POR_SEG = 60.0
DRIFT_COMBO_MAX = 8
DRIFT_COMBO_STEP = 1.0
DRIFT_EMISSAO_QPS = 28.0

# ---------- Física de Drift (tuning) ----------
DRIFT_ATRITO_GERAL       = 0.992
DRIFT_ATRITO_DERRAPANDO  = 0.985
DRIFT_GIRO_RESP          = 1.25
DRIFT_PERP_K             = 0.0065

VEL_MAX                  = 3.5  # Reduzido de 5.2 para 3.5
ACEL_BASE                = 0.08  # Reduzido de 0.12 para 0.08

# ---------- Turbo ----------
TURBO_FORCA_IMPULSO = 4.2
TURBO_FATOR        = 1.25
TURBO_DURACAO_S    = 0.9
TURBO_COOLDOWN_S   = 2.5

# ---------- Configurações de Opções ----------
# Configurações padrão
CONFIGURACOES = {
    "audio": {
        "volume_master": 1.0,
        "volume_musica": 0.8,
        "volume_efeitos": 0.9,
        "audio_habilitado": True,
        "musica_habilitada": True,
        "musica_no_menu": True,
        "musica_no_jogo": True,
        "musica_aleatoria": False
    },
    "video": {
        "resolucao": (1280, 720),
        "fullscreen": False,
        "tela_cheia_sem_bordas": False,
        "vsync": True,
        "fps_max": 60,
        "qualidade_alta": True
    },
    "controles": {
        "sensibilidade_volante": 1.0,
        "inverter_volante": False,
        "auto_centro": True
    },
    "jogo": {
        "dificuldade_ia": 1.0,
        "modo_drift": True,
        "mostrar_fps": False,
        "mostrar_debug": False
    }
}

# Caminho para salvar configurações
CAMINHO_CONFIG = os.path.join(DIR_PROJETO, "data", "config.json")

def carregar_configuracoes():
    """Carrega configurações do arquivo JSON"""
    import json
    try:
        if os.path.exists(CAMINHO_CONFIG):
            with open(CAMINHO_CONFIG, 'r', encoding='utf-8') as f:
                config_carregada = json.load(f)
                # Mesclar com configurações padrão
                for categoria, opcoes in config_carregada.items():
                    if categoria in CONFIGURACOES:
                        CONFIGURACOES[categoria].update(opcoes)
    except Exception as e:
        print(f"Erro ao carregar configurações: {e}")

def salvar_configuracoes():
    """Salva configurações no arquivo JSON"""
    import json
    try:
        with open(CAMINHO_CONFIG, 'w', encoding='utf-8') as f:
            json.dump(CONFIGURACOES, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")

# Carregar configurações ao importar
carregar_configuracoes()