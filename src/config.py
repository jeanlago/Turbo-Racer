import os
import glob

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
DIR_ICONS = os.path.join(DIR_PROJETO, "assets", "images", "icons")
CAMINHO_MENU = os.path.join(DIR_PROJETO, "assets", "images", "ui", "Menu.png")
CAMINHO_OFICINA = os.path.join(DIR_PROJETO, "assets", "images", "ui", "oficina.png")
CAMINHO_TROFEU_OURO = os.path.join(DIR_ICONS, "trofeu_ouro.png")
CAMINHO_TROFEU_PRATA = os.path.join(DIR_ICONS, "trofeu_prata.png")
CAMINHO_TROFEU_BRONZE = os.path.join(DIR_ICONS, "trofeu_bronze.png")
CAMINHO_TROFEU_VAZIO = os.path.join(DIR_ICONS, "trofeu_vazio.png")

# ---------- Sistema de Mapas ----------
def escanear_mapas_automaticamente():
    """Escaneia automaticamente a pasta maps e detecta mapas disponíveis"""
    mapas_detectados = {}
    
    # Verificar se a pasta maps existe
    if not os.path.exists(DIR_MAPS):
        print(f"Pasta de mapas não encontrada: {DIR_MAPS}")
        return mapas_detectados
    
    # Buscar todos os arquivos .png na pasta maps (exceto guides)
    padrao_mapa = os.path.join(DIR_MAPS, "*.png")
    arquivos_mapa = glob.glob(padrao_mapa)
    
    for arquivo_mapa in arquivos_mapa:
        nome_arquivo = os.path.basename(arquivo_mapa)
        nome_base = os.path.splitext(nome_arquivo)[0]
        
        # Pular arquivos que estão na subpasta guides
        if nome_base.endswith('_guides'):
            continue
            
        # Verificar se existe o arquivo de guias correspondente
        arquivo_guias = os.path.join(DIR_MAPS_GUIDES, f"{nome_base}_guides.png")
        arquivo_checkpoints = os.path.join(DIR_MAPS_GUIDES, f"{nome_base}_checkpoints.json")
        
        # Criar configuração do mapa
        mapa_config = {
            "nome": nome_base.replace("_", " ").title(),
            "arquivo_mapa": arquivo_mapa,
            "arquivo_guias": arquivo_guias,
            "arquivo_checkpoints": arquivo_checkpoints,
            "waypoints_fallback": [
                (640, 360), (800, 200), (1000, 400),
                (800, 600), (400, 600), (200, 400),
                (400, 200), (600, 300)
            ]  # Pontos de fallback genéricos
        }
        
        # Verificar se os arquivos existem
        arquivos_existentes = []
        if os.path.exists(arquivo_mapa):
            arquivos_existentes.append("mapa")
        if os.path.exists(arquivo_guias):
            arquivos_existentes.append("guias")
        if os.path.exists(arquivo_checkpoints):
            arquivos_existentes.append("checkpoints")
        
        # Adicionar mapa se pelo menos o arquivo principal existir
        if "mapa" in arquivos_existentes:
            mapas_detectados[nome_base] = mapa_config
            print(f"Mapa detectado: {nome_base} (arquivos: {', '.join(arquivos_existentes)})")
        else:
            print(f"Mapa ignorado: {nome_base} (arquivo principal não encontrado)")
    
    return mapas_detectados

# Escanear mapas automaticamente
MAPAS_DISPONIVEIS = escanear_mapas_automaticamente()

# Se nenhum mapa foi detectado, usar configuração padrão
if not MAPAS_DISPONIVEIS:
    print("Nenhum mapa detectado automaticamente, usando configuração padrão")
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
    }

# Mapa atual (pode ser alterado dinamicamente)
MAPA_ATUAL = list(MAPAS_DISPONIVEIS.keys())[0] if MAPAS_DISPONIVEIS else "Map_1"

# Funções para obter caminhos do mapa atual
def obter_caminho_mapa():
    if MAPA_ATUAL in MAPAS_DISPONIVEIS:
        return MAPAS_DISPONIVEIS[MAPA_ATUAL]["arquivo_mapa"]
    return os.path.join(DIR_MAPS, "Map_1.png")

def obter_caminho_guias():
    if MAPA_ATUAL in MAPAS_DISPONIVEIS:
        return MAPAS_DISPONIVEIS[MAPA_ATUAL]["arquivo_guias"]
    return os.path.join(DIR_MAPS_GUIDES, "Map_1_guides.png")

def obter_caminho_checkpoints():
    if MAPA_ATUAL in MAPAS_DISPONIVEIS:
        return MAPAS_DISPONIVEIS[MAPA_ATUAL]["arquivo_checkpoints"]
    return os.path.join(DIR_MAPS_GUIDES, "Map_1_checkpoints.json")


def recarregar_mapas():
    """Recarrega a lista de mapas escaneando novamente a pasta"""
    global MAPAS_DISPONIVEIS, MAPA_ATUAL
    mapas_anteriores = set(MAPAS_DISPONIVEIS.keys())
    MAPAS_DISPONIVEIS = escanear_mapas_automaticamente()
    mapas_novos = set(MAPAS_DISPONIVEIS.keys())
    
    # Verificar se há mapas novos
    mapas_adicionados = mapas_novos - mapas_anteriores
    mapas_removidos = mapas_anteriores - mapas_novos
    
    if mapas_adicionados:
        print(f"Mapas adicionados: {', '.join(mapas_adicionados)}")
    if mapas_removidos:
        print(f"Mapas removidos: {', '.join(mapas_removidos)}")
    
    # Se o mapa atual foi removido, trocar para o primeiro disponível
    if MAPA_ATUAL not in MAPAS_DISPONIVEIS and MAPAS_DISPONIVEIS:
        MAPA_ATUAL = list(MAPAS_DISPONIVEIS.keys())[0]
        print(f"Mapa atual alterado para: {MAPA_ATUAL}")
    
    # Atualizar caminhos após recarregar
    atualizar_caminhos_mapa()
    
    return len(mapas_adicionados) > 0 or len(mapas_removidos) > 0

def obter_lista_mapas():
    """Retorna lista de mapas disponíveis para o menu"""
    return list(MAPAS_DISPONIVEIS.keys())

def obter_nome_mapa(mapa_id):
    """Retorna o nome amigável de um mapa"""
    if mapa_id in MAPAS_DISPONIVEIS:
        return MAPAS_DISPONIVEIS[mapa_id]["nome"]
    return mapa_id

# Compatibilidade com código existente - serão atualizadas dinamicamente
CAMINHO_MAPA = obter_caminho_mapa()
CAMINHO_GUIAS = obter_caminho_guias()
CAMINHO_WAYPOINTS_JSON = obter_caminho_checkpoints()

def atualizar_caminhos_mapa():
    """Atualiza as variáveis globais de caminho quando o mapa é trocado"""
    global CAMINHO_MAPA, CAMINHO_GUIAS, CAMINHO_WAYPOINTS_JSON
    CAMINHO_MAPA = obter_caminho_mapa()
    CAMINHO_GUIAS = obter_caminho_guias()
    CAMINHO_WAYPOINTS_JSON = obter_caminho_checkpoints()
    
    # Sistema antigo de pista removido - cache não é mais necessário

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

PP_V_MIN = 60.0   # Aumentado de 50.0 para 60.0
PP_V_MAX = 250.0  # Aumentado de 200.0 para 250.0
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
CAMINHO_FUMACA = os.path.join(DIR_EFFECTS, "smoke", "pixels_00.png")  # coloque seu asset aqui

# ---------- Modo Drift / Pontuação ----------
MODO_DRIFT = True
DRIFT_MIN_VEL = 0.3  # Muito reduzido para permitir drift em velocidades baixas
DRIFT_PONTOS_BASE = 1.0
DRIFT_PONTOS_VEL_FACTOR = 0.06
DRIFT_DECAY_POR_SEG = 60.0
DRIFT_COMBO_MAX = 8
DRIFT_COMBO_STEP = 1.0
DRIFT_EMISSAO_QPS = 40.0

# ---------- Física de Drift (tuning) ----------
DRIFT_ATRITO_GERAL       = 0.992
DRIFT_ATRITO_DERRAPANDO  = 0.985
DRIFT_GIRO_RESP          = 1.25
DRIFT_PERP_K             = 0.0065

VEL_MAX                  = 3.0  # Reduzido para velocidade mais realista
ACEL_BASE                = 0.06  # Reduzido para aceleração mais suave

# ---------- Turbo ----------
TURBO_FORCA_IMPULSO = 4.0  # Aumentado para dar mais impulso
TURBO_FATOR        = 200.0  # Aumentado para 200.0x (19900% de boost) - EXTREMAMENTE PODEROSO
TURBO_DURACAO_S    = 1.2   # Aumentado de 0.9 para 1.2 (dura mais tempo)
TURBO_COOLDOWN_S   = 3.0   # Aumentado de 2.5 para 3.0 (cooldown maior)

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
        "vsync": False,  # Desabilitado para melhor FPS
        "fps_max": 120,  # Reduzido para 120 FPS para melhor performance
        "qualidade_alta": False,  # Padrão para melhor performance
        "mostrar_fps": True  # Habilitado para monitorar performance
    },
    "controles": {
        "sensibilidade_volante": 1.0,
        "inverter_volante": False,
        "auto_centro": True
    },
    "jogo": {
        "dificuldade_IA": 1.0,
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