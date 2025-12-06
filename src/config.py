import os
import sys
import glob
import contextlib

if not hasattr(sys.stderr, '_filtered_libpng'):
    class FilteredStderr:
        """Filtra avisos do libpng sobre iCCP do stderr"""
        def __init__(self, original_stderr):
            self.original_stderr = original_stderr
            self._filtered_libpng = True
        
        def write(self, message):
            if message:
                msg_lower = message.lower()
                if 'libpng warning' in msg_lower and 'iCCP' in message:
                    return
                if 'iCCP' in message and ('known incorrect' in msg_lower or 'sRGB profile' in msg_lower):
                    return
            self.original_stderr.write(message)
        
        def flush(self):
            self.original_stderr.flush()
        
        def __getattr__(self, name):
            return getattr(self.original_stderr, name)
    
    sys.stderr = FilteredStderr(sys.stderr)

LARGURA, ALTURA = 1280, 720
FPS = 60

# Modo de teste: marca corridas como concluídas automaticamente ao clicar
MODO_TESTE_CORRIDAS = False  # Altere para False para desativar

def obter_caminho_base():
    """Retorna o caminho base do projeto, funcionando tanto em dev quanto no executável"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    return base_path

def obter_caminho_projeto():
    """Retorna o caminho do projeto, funcionando tanto em dev quanto no executável"""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DIR_BASE = obter_caminho_base()
DIR_PROJETO = obter_caminho_projeto()
DIR_SPRITES = os.path.join(DIR_PROJETO, "assets", "images", "cars")
DIR_CAR_SELECTION = os.path.join(DIR_PROJETO, "assets", "images", "car_selection")
DIR_MAPS = os.path.join(DIR_PROJETO, "assets", "images", "maps")
DIR_MAPS_GUIDES = os.path.join(DIR_MAPS, "guides")
DIR_ICONS = os.path.join(DIR_PROJETO, "assets", "images", "icons")
DIR_UI = os.path.join(DIR_PROJETO, "assets", "images", "ui")
CAMINHO_MENU = os.path.join(DIR_UI, "Menu.png")
CAMINHO_OFICINA = os.path.join(DIR_UI, "oficina.png")
CAMINHO_TROFEU_OURO = os.path.join(DIR_ICONS, "trofeu_ouro.png")
CAMINHO_TROFEU_PRATA = os.path.join(DIR_ICONS, "trofeu_prata.png")
CAMINHO_TROFEU_BRONZE = os.path.join(DIR_ICONS, "trofeu_bronze.png")
CAMINHO_TROFEU_VAZIO = os.path.join(DIR_ICONS, "trofeu_vazio.png")

_estado_dia_noite = "dia"

def definir_estado_dia_noite(estado: str):
    """Define o estado atual do ciclo dia/noite
    
    Args:
        estado: "dia" ou "noite"
    """
    global _estado_dia_noite
    if estado.lower() in ("dia", "noite"):
        _estado_dia_noite = estado.lower()
    else:
        print(f"AVISO: Estado dia/noite inválido: {estado}. Usando 'dia'.")
        _estado_dia_noite = "dia"

def obter_estado_dia_noite() -> str:
    """Retorna o estado atual do ciclo dia/noite
    
    Returns:
        "dia" ou "noite"
    """
    return _estado_dia_noite

def alternar_dia_noite():
    """Alterna entre dia e noite"""
    global _estado_dia_noite
    _estado_dia_noite = "noite" if _estado_dia_noite == "dia" else "dia"

def obter_caminho_sprite_dia_noite(nome_base: str, diretorio: str = None, extensao: str = ".png") -> str:
    """Obtém o caminho correto de um sprite baseado no ciclo dia/noite
    
    Tenta carregar o sprite com sufixo _dia ou _noite. Se não existir, tenta o nome base.
    Se ainda não existir, retorna o caminho do sprite padrão.
    
    Args:
        nome_base: Nome base do arquivo (sem sufixo _dia/_noite e sem extensão)
        diretorio: Diretório onde o arquivo está (padrão: DIR_UI)
        extensao: Extensão do arquivo (padrão: ".png")
    
    Returns:
        Caminho completo do arquivo sprite
    """
    if diretorio is None:
        diretorio = DIR_UI
    
    estado = obter_estado_dia_noite()
    sufixo = "_dia" if estado == "dia" else "_noite"
    
    caminho_com_sufixo = os.path.join(diretorio, f"{nome_base}{sufixo}{extensao}")
    if os.path.exists(caminho_com_sufixo):
        return caminho_com_sufixo
    
    # Se é noite e o arquivo noite não existe, tentar arquivo dia como fallback
    if estado == "noite":
        caminho_dia = os.path.join(diretorio, f"{nome_base}_dia{extensao}")
        if os.path.exists(caminho_dia):
            return caminho_dia
    
    caminho_base = os.path.join(diretorio, f"{nome_base}{extensao}")
    if os.path.exists(caminho_base):
        return caminho_base
    
    return caminho_com_sufixo

@contextlib.contextmanager
def suppress_libpng_warnings():
    """Context manager para suprimir avisos do libpng sobre iCCP"""
    import sys
    from io import StringIO
    old_stderr = sys.stderr
    try:
        sys.stderr = StringIO()
        yield
    finally:
        sys.stderr = old_stderr

def obter_caminho_hover_dia_noite(caminho_hover: str) -> str:
    """Obtém o caminho correto de um hover sprite baseado no ciclo dia/noite
    
    Tenta carregar o hover com sufixo _dia ou _noite. Se não existir, tenta o nome base.
    
    Args:
        caminho_hover: Caminho completo do arquivo hover (pode ser relativo ou absoluto)
    
    Returns:
        Caminho completo do arquivo hover (dia/noite ou fallback)
    """
    if not os.path.isabs(caminho_hover):
        caminho_hover = os.path.join(DIR_PROJETO, caminho_hover)
    
    caminho_hover = caminho_hover.replace("\\", os.sep).replace("/", os.sep)
    
    diretorio = os.path.dirname(caminho_hover)
    nome_completo = os.path.basename(caminho_hover)
    nome_base, extensao = os.path.splitext(nome_completo)
    
    estado = obter_estado_dia_noite()
    sufixo = "_dia" if estado == "dia" else "_noite"
    
    caminho_com_sufixo = os.path.join(diretorio, f"{nome_base}{sufixo}{extensao}")
    if os.path.exists(caminho_com_sufixo):
        return caminho_com_sufixo
    
    if os.path.exists(caminho_hover):
        return caminho_hover
    
    return caminho_com_sufixo

def escanear_mapas_automaticamente():
    """Escaneia automaticamente a pasta maps e detecta mapas disponíveis"""
    mapas_detectados = {}
    
    if not os.path.exists(DIR_MAPS):
        print(f"Pasta de mapas não encontrada: {DIR_MAPS}")
        return mapas_detectados
    
    padrao_mapa = os.path.join(DIR_MAPS, "*.png")
    arquivos_mapa = glob.glob(padrao_mapa)
    
    for arquivo_mapa in arquivos_mapa:
        nome_arquivo = os.path.basename(arquivo_mapa)
        nome_base = os.path.splitext(nome_arquivo)[0]
        
        if nome_base.endswith('_guides'):
            continue
            
        arquivo_guias = os.path.join(DIR_MAPS_GUIDES, f"{nome_base}_guides.png")
        arquivo_checkpoints = os.path.join(DIR_MAPS_GUIDES, f"{nome_base}_checkpoints.json")
        
        mapa_config = {
            "nome": nome_base.replace("_", " ").title(),
            "arquivo_mapa": arquivo_mapa,
            "arquivo_guias": arquivo_guias,
            "arquivo_checkpoints": arquivo_checkpoints,
            "waypoints_fallback": [
                (640, 360), (800, 200), (1000, 400),
                (800, 600), (400, 600), (200, 400),
                (400, 200), (600, 300)
            ]
        }
        
        arquivos_existentes = []
        if os.path.exists(arquivo_mapa):
            arquivos_existentes.append("mapa")
        if os.path.exists(arquivo_guias):
            arquivos_existentes.append("guias")
        if os.path.exists(arquivo_checkpoints):
            arquivos_existentes.append("checkpoints")
        
        if "mapa" in arquivos_existentes:
            mapas_detectados[nome_base] = mapa_config
            print(f"Mapa detectado: {nome_base} (arquivos: {', '.join(arquivos_existentes)})")
        else:
            print(f"Mapa ignorado: {nome_base} (arquivo principal não encontrado)")
    
    return mapas_detectados

MAPAS_DISPONIVEIS = escanear_mapas_automaticamente()

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

MAPA_ATUAL = list(MAPAS_DISPONIVEIS.keys())[0] if MAPAS_DISPONIVEIS else "Map_1"

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
    
    mapas_adicionados = mapas_novos - mapas_anteriores
    mapas_removidos = mapas_anteriores - mapas_novos
    
    if mapas_adicionados:
        print(f"Mapas adicionados: {', '.join(mapas_adicionados)}")
    if mapas_removidos:
        print(f"Mapas removidos: {', '.join(mapas_removidos)}")
    
    if MAPA_ATUAL not in MAPAS_DISPONIVEIS and MAPAS_DISPONIVEIS:
        MAPA_ATUAL = list(MAPAS_DISPONIVEIS.keys())[0]
        print(f"Mapa atual alterado para: {MAPA_ATUAL}")
    
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

CAMINHO_MAPA = obter_caminho_mapa()
CAMINHO_GUIAS = obter_caminho_guias()
CAMINHO_WAYPOINTS_JSON = obter_caminho_checkpoints()

def atualizar_caminhos_mapa():
    """Atualiza as variáveis globais de caminho quando o mapa é trocado"""
    global CAMINHO_MAPA, CAMINHO_GUIAS, CAMINHO_WAYPOINTS_JSON
    CAMINHO_MAPA = obter_caminho_mapa()
    CAMINHO_GUIAS = obter_caminho_guias()
    CAMINHO_WAYPOINTS_JSON = obter_caminho_checkpoints()

CORES_PISTA = [(31, 23, 38), (0, 0, 0), (240, 224, 0), (144, 105, 0)]
TOLERANCIA_COR = 18
HSV_S_MAX = 45
HSV_V_MAX = 55

VOLTAS_OBJETIVO = 3
LINHA_LARGADA = (498, 93, 28, 130)
PONTOS_DE_CONTROLE = [(160, 520, 40, 120), (880, 630, 40, 120), (900, 180, 40, 120)]

TURBO_P1 = "K_LSHIFT"
TURBO_P2 = "K_RCTRL"

COR_TEXTO = (255, 255, 255)
COR_SOMBRA = (0, 0, 0)

USAR_IA_NO_CARRO_2 = False

TRILHAS_IA = [
    {"cor": (255, 170, 60), "tol": 40},
]

CHECKPOINT_COR = (255, 0, 255)
CHECKPOINT_TOL = 50
CHECKPOINT_MIN_PIXELS = 60

WAYPOINTS_MAP_1 = [
    (820, 140), (930, 360), (860, 620),
    (520, 650), (200, 600), (160, 420),
    (260, 150), (500, 120)
]

PP_WHEELBASE = 36.0
PP_LD_MIN = 60.0
PP_LD_MAX = 200.0
PP_LD_KV  = 1.5

PP_V_MIN = 60.0
PP_V_MAX = 250.0
PP_K_CURV_SPEED = 120.0

PP_BRAKE_EPS = 25.0
PP_ACCEL_GAIN = 1.2
PP_BRAKE_GAIN = 1.0
PP_STEER_GAIN = 1.0
PP_STEER_DEADZONE = 0.08

PP_STUCK_EPS_V = 8.0
PP_STUCK_TIME  = 0.7
PP_RECOVER_TIME = 0.6
PP_RECOVER_STEER_DEG = 28

DIR_EFFECTS = os.path.join(DIR_PROJETO, "assets", "images", "effects")
CAMINHO_FUMACA = os.path.join(DIR_EFFECTS, "smoke", "pixels_00.png")

MODO_DRIFT = True
DRIFT_MIN_VEL = 0.3
DRIFT_PONTOS_BASE = 1.0
DRIFT_PONTOS_VEL_FACTOR = 0.06
DRIFT_DECAY_POR_SEG = 60.0
DRIFT_COMBO_MAX = 8
DRIFT_COMBO_STEP = 1.0
DRIFT_EMISSAO_QPS = 40.0

DRIFT_ATRITO_GERAL       = 0.992
DRIFT_ATRITO_DERRAPANDO  = 0.985
DRIFT_GIRO_RESP          = 1.25
DRIFT_PERP_K             = 0.0065

VEL_MAX                  = 3.0
ACEL_BASE                = 0.06

TURBO_FORCA_IMPULSO = 4.0
TURBO_FATOR        = 200.0
TURBO_DURACAO_S    = 1.2
TURBO_COOLDOWN_S   = 3.0

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
        "vsync": False,
        "fps_max": 120,
        "qualidade_alta": False,
        "mostrar_fps": True
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
        "mostrar_debug": False,
        "confirmar_upgrade": True
    },
    "idioma": {
        "idioma_atual": "pt"
    }
}

CAMINHO_CONFIG = os.path.join(DIR_PROJETO, "data", "config.json")

def carregar_configuracoes():
    """Carrega configurações do arquivo JSON"""
    import json
    try:
        if os.path.exists(CAMINHO_CONFIG):
            with open(CAMINHO_CONFIG, 'r', encoding='utf-8') as f:
                config_carregada = json.load(f)
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

carregar_configuracoes()