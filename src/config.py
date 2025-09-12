import os

# ---------- Tela ----------
LARGURA, ALTURA = 1280, 720
FPS = 60

# ---------- Caminhos ----------
DIR_BASE = os.path.dirname(__file__)
DIR_PROJETO = os.path.abspath(os.path.join(DIR_BASE, ".."))
DIR_SPRITES = os.path.join(DIR_PROJETO, "assets", "images", "car_sprites")
CAMINHO_MAPA = os.path.join(DIR_PROJETO, "assets", "images", "maps", "Map_1.png")
CAMINHO_GUIAS = os.path.join(DIR_PROJETO, "assets", "images", "maps", "guides", "Map_1_guides.png")

# >>> arquivo onde salvaremos a rota gravada
CAMINHO_WAYPOINTS_JSON = os.path.join(
    DIR_PROJETO, "assets", "images", "maps", "guides", "Map_1_guides.json"
)

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

PP_V_MIN = 70.0
PP_V_MAX = 280.0
PP_K_CURV_SPEED = 180.0

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

VEL_MAX                  = 5.2
ACEL_BASE                = 0.12

# ---------- Turbo ----------
TURBO_FORCA_IMPULSO = 4.2
TURBO_FATOR        = 1.25
TURBO_DURACAO_S    = 0.9
TURBO_COOLDOWN_S   = 2.5