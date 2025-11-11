# 🔧 API Reference - Turbo Racer

Referência completa da API do Turbo Racer v2.1.0.

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Classes Principais](#classes-principais)
4. [Sistemas de Jogo](#sistemas-de-jogo)
5. [Configuração](#configuração)
6. [Exemplos](#exemplos)
7. [Troubleshooting](#troubleshooting)

---

## Visão Geral

O Turbo Racer é um jogo de corrida arcade 2D desenvolvido em Python com Pygame, oferecendo:

- **Física realista** de veículos com 3 tipos de tração (RWD, FWD, AWD)
- **IA inteligente** usando algoritmo Pure Pursuit para navegação
- **Múltiplos modos** de jogo (1 jogador, 2 jogadores split-screen, drift)
- **Sistema escalável** de mapas com detecção automática
- **Interface modular** e altamente configurável
- **Sistema de drift** com pontuação e combos
- **Editor visual** de checkpoints integrado

### Tecnologias
- **Python 3.10+** - Linguagem principal
- **Pygame 2.5+** - Renderização e input
- **JSON** - Configurações e dados persistentes
- **NumPy** - Cálculos matemáticos (opcional)

---

## Arquitetura

### Estrutura de Módulos

```
src/
├── main.py                 # Ponto de entrada e loop principal
├── config.py              # Configurações globais e constantes
└── core/
    ├── carro_fisica.py    # Sistema de física avançada (principal)
    ├── pista.py           # Detecção de pista e colisões
    ├── camera.py          # Sistema de câmera dinâmica
    ├── corrida.py         # Gerenciamento de corrida
    ├── ia.py              # Inteligência artificial (Pure Pursuit)
    ├── checkpoint_manager.py # Editor visual de checkpoints
    ├── menu.py            # Sistema de menus completo
    ├── hud.py             # Sistema de HUD dinâmico
    ├── musica.py          # Gerenciador de música
    ├── particulas.py      # Efeitos de partículas
    ├── skidmarks.py       # Sistema de marcas de pneu
    ├── drift_scoring.py   # Sistema de pontuação de drift
    └── game_modes.py      # Enums para modos de jogo
```

---

## Classes Principais

### `CarroFisica` - Sistema de Física Principal

```python
class CarroFisica:
    def __init__(self, x, y, prefixo_cor, controles, turbo_key=None, nome="", tipo_tracao="RWD")
    def atualizar(self, teclas, superficie_mascara, dt)
    def desenhar(self, superficie, camera=None)
    def usar_turbo(self)
    def ativar_drift(self)
    def desativar_drift(self)
    def _atualizar_fisica(self, acelerar, direita, esquerda, frear, turbo_pressed, superficie_mascara, dt)
```

**Propriedades:**
- `x`, `y` - Posição no mundo
- `angulo` - Orientação em graus
- `vx`, `vy` - Velocidades
- `turbo_carga` - Carga de turbo (0-100)
- `drift_ativado` - Estado do drift
- `tipo_tracao` - Tipo de tração (RWD/FWD/AWD)
- `skidmarks` - Sistema de marcas de pneu

### `Camera` - Sistema de Câmera Dinâmica

```python
class Camera:
    def __init__(self, largura_tela, altura_tela, largura_mundo, altura_mundo, zoom=1.0)
    def set_alvo(self, alvo)
    def atualizar(self, dt)
    def mundo_para_tela(self, x, y)
    def tela_para_mundo(self, x, y)
    def desenhar_fundo(self, superficie, imagem)
    def esta_visivel(self, x, y, raio)
```

**Propriedades:**
- `cx`, `cy` - Centro da câmera no mundo
- `zoom` - Nível de zoom atual
- `alvo` - Objeto que a câmera segue
- `largura_tela`, `altura_tela` - Dimensões da tela
- `largura_mundo`, `altura_mundo` - Dimensões do mundo

### `IA` - Inteligência Artificial (Pure Pursuit)

```python
class IA:
    def __init__(self, checkpoints, nome="IA")
    def controlar(self, carro, mask_guias, is_on_track, dt)
    def desenhar_debug(self, superficie, camera=None, mostrar_todos_checkpoints=False)
    def _calcular_steering_angle(self, carro, ponto_alvo)
    def _encontrar_ponto_lookahead(self, carro, checkpoints)
```

**Propriedades:**
- `checkpoints` - Lista de pontos de navegação
- `nome` - Nome identificador da IA
- `debug` - Modo de debug visual
- `ponto_alvo` - Ponto atual de destino
- `lookahead_distance` - Distância de antecipação

### `HUD` - Sistema de Interface

```python
class HUD:
    def __init__(self)
    def desenhar_hud_completo(self, superficie, carro)
    def desenhar_velocimetro(self, superficie, carro)
    def desenhar_nitro(self, superficie, carro)
    def desenhar_informacoes_carro(self, superficie, carro)
```

**Elementos do HUD:**
- Velocímetro horizontal com PNGs (número de velocidade + barra animada)
- Indicador de nitro (posicionado ao lado do velocímetro)
- Informações do carro
- Debug de física (opcional)

---

## Sistemas de Jogo

### Modos de Jogo

```python
class ModoJogo(Enum):
    UM_JOGADOR = "1_jogador"
    DOIS_JOGADORES = "2_jogadores"

class TipoJogo(Enum):
    CORRIDA = "corrida"
    DRIFT = "drift"
```

**Características dos Modos:**
- **1 Jogador:** Câmera dinâmica, competição contra IA
- **2 Jogadores:** Split-screen, câmeras independentes
- **Corrida:** Sistema de checkpoints, vitória por completar volta
- **Drift:** Sistema de pontuação, tempo limitado (2 min)

### Sistema de Drift

```python
class DriftScoring:
    def __init__(self):
        self.pontuacao_total = 0
        self.combo_atual = 0
        self.tempo_combo = 0.0
        self.velocidade_minima = 2.0
        self.angulo_minimo = 15.0
    
    def update(self, dt, angulo_drift, velocidade_kmh, x, y, drift_ativado, derrapando, collision_force=0.0)
    def draw_hud(self, superficie, x, y, fonte)
```

**Mecânicas de Pontuação:**
- **Velocidade mínima:** 2.0 para pontuar
- **Ângulo mínimo:** 15° para considerar drift
- **Sistema de combo:** Multiplicador por derrapagens consecutivas
- **Decay automático:** Pontos diminuem sem drift contínuo

### Sistema de Checkpoints

```python
class CheckpointManager:
    def __init__(self, mapa_atual=None)
    def adicionar_checkpoint(self, x, y)
    def adicionar_checkpoint_na_posicao(self, screen_x, screen_y, camera)
    def remover_checkpoint(self, indice)
    def mover_checkpoint(self, indice, novo_x, novo_y)
    def encontrar_checkpoint_proximo(self, x, y, raio)
    def salvar_checkpoints(self)
    def carregar_checkpoints(self)
    def desenhar(self, superficie, camera)
    def processar_teclado(self, teclas)
    def processar_teclas_f(self, teclas)
```

**Funcionalidades:**
- **Editor visual** - Clique e arraste para mover
- **Adição dinâmica** - Ctrl+clique para adicionar
- **Salvamento automático** - F5 para salvar
- **Modo edição** - F7 para ativar/desativar
- **Debug visual** - F10 para mostrar todos

---

## Configuração

### Carros Disponíveis

```python
CARROS_DISPONIVEIS = [
    {
        "nome": "Nissan 350Z",
        "prefixo_cor": "Car1",
        "tipo_tracao": "rear",  # RWD
        "sprite_selecao": "Car1",
        "tamanho_oficina": (850, 550),
        "posicao_oficina": (LARGURA//2 - 430, 170)
    },
    {
        "nome": "BMW M3 95'",
        "prefixo_cor": "Car2",
        "tipo_tracao": "rear",  # RWD
        "sprite_selecao": "Car2",
        "tamanho_oficina": (600, 300),
        "posicao_oficina": (LARGURA//2 - 300, 380)
    }
    # ... 10 carros adicionais
]
```

**Tipos de Tração:**
- `"rear"` - Tração traseira (RWD) - Pode fazer drift
- `"front"` - Tração frontal (FWD) - Estável, sem drift
- `"awd"` - Tração integral (AWD) - Equilibrado

### Configurações de Física

```python
# Em config.py
VEL_MAX = 3.5              # Velocidade máxima
ACEL_BASE = 0.08           # Aceleração base
ATRITO_GERAL = 0.992       # Atrito geral
ATRITO_DERRAPANDO = 0.985  # Atrito durante drift
TURBO_DURACAO = 0.9        # Duração do turbo (segundos)
TURBO_COOLDOWN = 2.5       # Cooldown do turbo (segundos)
TURBO_MULTIPLICADOR = 1.25 # Multiplicador de velocidade
```

### Configurações de IA

```python
# Parâmetros Pure Pursuit
PP_WHEELBASE = 36.0        # Distância entre eixos
PP_LD_MIN = 60             # Lookahead distance mínima
PP_LD_MAX = 200            # Lookahead distance máxima
PP_V_MIN = 50              # Velocidade mínima
PP_V_MAX = 200             # Velocidade máxima
PP_GAIN = 0.8              # Ganho de direção
```

### Sistema de Mapas

```python
# Detecção automática de mapas
def escanear_mapas_automaticamente():
    """Escaneia automaticamente a pasta maps"""
    # Detecta arquivos .png na pasta assets/images/maps/
    # Gera nomes amigáveis automaticamente
    # Verifica arquivos de guias e checkpoints
```

---

## Exemplos

### Criando um Carro

```python
# Carro com física avançada
carro = CarroFisica(
    x=100, y=100,
    prefixo_cor="Car1",
    controles=(pygame.K_w, pygame.K_d, pygame.K_a, pygame.K_s),
    turbo_key=pygame.K_LSHIFT,
    nome="Jogador 1",
    tipo_tracao="rear"  # RWD
)
```

### Configurando IA

```python
# IA com checkpoints
checkpoints = [(100, 100), (200, 200), (300, 300)]
ia = IA(checkpoints, nome="IA-1")

# Controlar carro
ia.controlar(carro, mask_guias, is_on_track, dt)
```

### Sistema de Câmera Dinâmica

```python
# Câmera que segue o carro
camera = Camera(LARGURA, ALTURA, LARGURA_MUNDO, ALTURA_MUNDO)
camera.set_alvo(carro)

# Atualizar câmera dinâmica (zoom baseado na velocidade)
velocidade = math.sqrt(carro.vx**2 + carro.vy**2)
if velocidade < 30:
    zoom = 1.4 - (velocidade / 30) * 0.3
elif velocidade < 80:
    zoom = 1.1 - ((velocidade - 30) / 50) * 0.3
else:
    zoom = 0.8 - min((velocidade - 80) / 120, 1.0) * 0.1

camera.zoom += (zoom - camera.zoom) * dt * 0.8
```

### Sistema de Drift

```python
# Configurar sistema de drift
drift_scoring = DriftScoring()

# Atualizar pontuação durante o jogo
vlong, vlat = carro._mundo_para_local(carro.vx, carro.vy)
velocidade_kmh = abs(vlong) * 1.0 * (200.0 / 650.0)
angulo_drift = abs(math.degrees(math.atan2(vlat, max(0.1, abs(vlong)))))

drift_scoring.update(
    dt,
    angulo_drift,
    velocidade_kmh,
    carro.x,
    carro.y,
    carro.drift_ativado,
    carro.drifting,
    collision_force=0.0
)
```

### Modo 2 Jogadores (Split-Screen)

```python
# Configurar modo 2 jogadores
modo_jogo = ModoJogo.DOIS_JOGADORES
tipo_jogo = TipoJogo.CORRIDA

# Criar carros
carro1 = CarroFisica(100, 100, "Car1", controles_p1, tipo_tracao="rear")
carro2 = CarroFisica(200, 100, "Car2", controles_p2, tipo_tracao="rear")

# Renderizar split-screen
metade_largura = LARGURA // 2
superficie_p1 = pygame.Surface((metade_largura, ALTURA))
superficie_p2 = pygame.Surface((metade_largura, ALTURA))

# Câmeras independentes
camera_p1 = Camera(metade_largura, ALTURA, LARGURA_MUNDO, ALTURA_MUNDO)
camera_p2 = Camera(metade_largura, ALTURA, LARGURA_MUNDO, ALTURA_MUNDO)

# Renderizar cada metade
camera_p1.set_alvo(carro1)
camera_p1.desenhar_fundo(superficie_p1, img_pista)
carro1.desenhar(superficie_p1, camera=camera_p1)

camera_p2.set_alvo(carro2)
camera_p2.desenhar_fundo(superficie_p2, img_pista)
carro2.desenhar(superficie_p2, camera=camera_p2)

# Combinar na tela principal
tela.blit(superficie_p1, (0, 0))
tela.blit(superficie_p2, (metade_largura, 0))
```

---

## Troubleshooting

### Problemas Comuns

**IA não segue checkpoints:**
- Verificar se checkpoints estão salvos (F5)
- Verificar se arquivo JSON existe em `data/`
- Usar modo debug (F1) para visualizar
- Verificar se checkpoints estão na pista válida

**Carro não responde aos controles:**
- Verificar se modo de edição está desativado (F7)
- Verificar configuração de teclas no `main.py`
- Verificar se corrida foi iniciada
- Verificar se jogo não está pausado (ESC)

**Câmera tremula:**
- Reduzir velocidade de interpolação em `camera.py`
- Verificar se `dt` está sendo calculado corretamente
- Ajustar limites de zoom (0.7 - 1.4)
- Verificar se `dt` não é muito alto

**Performance baixa:**
- Reduzir FPS máximo nas configurações
- Desativar efeitos visuais (qualidade_alta = false)
- Reduzir resolução
- Desativar debug da IA (F1)

**Mapas não aparecem:**
- Verificar se arquivo PNG está em `assets/images/maps/`
- Pressionar R para recarregar mapas
- Verificar formato do arquivo (PNG com transparência)
- Verificar se nome do arquivo não tem caracteres especiais

### Debug

- **F1** - Ativar/desativar debug da IA
- **H** - Alternar HUD completo
- **F7** - Modo edição de checkpoints
- **F10** - Mostrar todos os checkpoints

### Controles de Carro

- **Jogador 1:** WASD + Shift (turbo) + Espaço (drift)
- **Jogador 2:** Setas + Ctrl (turbo) + Shift (drift)
- **Música:** M (próxima) / N (anterior)
- **Menu:** ESC (pausar/voltar)

---

**Versão:** 2.1.0  
**Última atualização:** Dezembro 2024  
**Desenvolvedores:** Jean Marins e Jayson Sales
