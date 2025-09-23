# 🔧 API Reference - Turbo Racer

Referência completa da API do Turbo Racer.

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Classes Principais](#classes-principais)
4. [Sistemas de Jogo](#sistemas-de-jogo)
5. [Configuração](#configuração)
6. [Exemplos](#exemplos)

---

## Visão Geral

O Turbo Racer é um jogo de corrida 2D desenvolvido em Python com Pygame, oferecendo:

- **Física realista** de veículos com derrapagem
- **IA inteligente** usando algoritmo Pure Pursuit
- **Múltiplos modos** de jogo (1/2 jogadores, drift)
- **Sistema escalável** de mapas e carros
- **Interface modular** e configurável

### Tecnologias
- **Python 3.10+**
- **Pygame** - Renderização e input
- **JSON** - Configurações e dados

---

## Arquitetura

### Estrutura de Módulos

```
src/
├── main.py                 # Ponto de entrada e loop principal
├── config.py              # Configurações globais
└── core/
    ├── carro.py           # Física e controle dos veículos
    ├── carro_fisica.py    # Sistema de física avançada
    ├── pista.py           # Detecção de pista e colisões
    ├── camera.py          # Sistema de câmera
    ├── corrida.py         # Gerenciamento de corrida
    ├── ia.py              # Inteligência artificial
    ├── checkpoint_manager.py # Editor de checkpoints
    ├── menu.py            # Sistema de menus
    ├── hud.py             # Sistema de HUD
    ├── game_modes.py      # Enums para modos de jogo
    └── drift_scoring.py   # Sistema de pontuação de drift
```

---

## Classes Principais

### `Carro` - Veículo Principal

```python
class Carro:
    def __init__(self, x, y, prefixo_cor, controles, turbo_key=None, nome="")
    def atualizar(self, teclas, superficie_mascara, dt)
    def desenhar(self, superficie, camera=None)
    def usar_turbo(self)
    def iniciar_drift(self)
    def parar_drift(self)
```

**Propriedades:**
- `x`, `y` - Posição no mundo
- `angulo` - Orientação em graus
- `vx`, `vy` - Velocidades
- `turbo_carga` - Carga de turbo (0-100)
- `drift_ativado` - Estado do drift

### `CarroFisica` - Sistema de Física

```python
class CarroFisica:
    def __init__(self, x, y, angulo, tipo_tracao="RWD")
    def _atualizar_fisica(self, acelerar, direita, esquerda, frear, turbo_pressed, superficie_mascara, dt)
    def _decomp_vel(self) -> tuple[float, float]
    def _recomp_vel(self, v_long: float, v_lat: float)
```

**Tipos de Tração:**
- `"RWD"` - Tração traseira (drift)
- `"FWD"` - Tração frontal (estável)
- `"AWD"` - Tração integral (equilibrado)

### `Camera` - Sistema de Câmera

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

### `IA` - Inteligência Artificial

```python
class IA:
    def __init__(self, checkpoints, nome="IA")
    def controlar(self, carro, mask_guias, is_on_track, dt)
    def desenhar_debug(self, superficie, camera=None)
    def _calcular_steering_angle(self, carro, ponto_alvo)
    def _encontrar_ponto_lookahead(self, carro, checkpoints)
```

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

### Sistema de Drift

```python
class DriftScoring:
    def __init__(self):
        self.pontuacao_total = 0
        self.combo_atual = 0
        self.tempo_combo = 0.0
    
    def atualizar(self, carro, dt)
    def desenhar_hud(self, superficie, x, y)
```

### Sistema de Checkpoints

```python
class CheckpointManager:
    def __init__(self, mapa_atual=None)
    def adicionar_checkpoint(self, x, y)
    def remover_checkpoint(self, indice)
    def mover_checkpoint(self, indice, novo_x, novo_y)
    def salvar_checkpoints(self)
    def carregar_checkpoints(self)
    def desenhar(self, superficie, camera)
```

---

## Configuração

### Carros Disponíveis

```python
CARROS_DISPONIVEIS = [
    {
        "nome": "Nissan 350Z",
        "prefixo_cor": "Nissan350Z",
        "tipo_tracao": "RWD",
        "sprite_selecao": "Nissan350Z",
        "tamanho_oficina": (100, 60),
        "posicao_oficina": (300, 150)
    }
    # ... mais carros
]
```

### Configurações de Física

```python
# Em config.py
VEL_MAX = 3.5              # Velocidade máxima
ACEL_BASE = 0.08           # Aceleração base
ATRITO_GERAL = 0.992       # Atrito geral
ATRITO_DERRAPANDO = 0.985  # Atrito durante drift
```

### Configurações de IA

```python
# Parâmetros Pure Pursuit
PP_WHEELBASE = 36.0        # Distância entre eixos
PP_LD_MIN = 60             # Lookahead distance mínima
PP_LD_MAX = 200            # Lookahead distance máxima
PP_V_MIN = 50              # Velocidade mínima
PP_V_MAX = 200             # Velocidade máxima
```

---

## Exemplos

### Criando um Carro

```python
# Carro básico
carro = Carro(
    x=100, y=100,
    prefixo_cor="Nissan350Z",
    controles={
        "acelerar": pygame.K_w,
        "frear": pygame.K_s,
        "esquerda": pygame.K_a,
        "direita": pygame.K_d
    },
    turbo_key=pygame.K_LSHIFT,
    nome="Jogador 1"
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

# Atualizar câmera dinâmica
velocidade = math.sqrt(carro.vx**2 + carro.vy**2)
if velocidade < 30:
    zoom = 1.4 - (velocidade / 30) * 0.3
elif velocidade < 80:
    zoom = 1.1 - ((velocidade - 30) / 50) * 0.3
else:
    zoom = 0.8 - min((velocidade - 80) / 120, 1.0) * 0.1

camera.zoom = camera.zoom + (zoom - camera.zoom) * dt * 0.8
```

### Modo 2 Jogadores

```python
# Configurar modo 2 jogadores
modo_jogo = ModoJogo.DOIS_JOGADORES
tipo_jogo = TipoJogo.CORRIDA

# Criar carros
carro1 = Carro(100, 100, "Nissan350Z", controles_p1)
carro2 = Carro(200, 100, "Nissan350Z", controles_p2)

# Renderizar split-screen
metade_largura = LARGURA // 2
superficie_p1 = pygame.Surface((metade_largura, ALTURA))
superficie_p2 = pygame.Surface((metade_largura, ALTURA))

# Câmeras independentes
camera_p1 = Camera(metade_largura, ALTURA, LARGURA_MUNDO, ALTURA_MUNDO)
camera_p2 = Camera(metade_largura, ALTURA, LARGURA_MUNDO, ALTURA_MUNDO)
```

---

## Troubleshooting

### Problemas Comuns

**IA não segue checkpoints:**
- Verificar se checkpoints estão salvos
- Verificar se arquivo JSON existe
- Usar modo debug (F1)

**Carro não responde aos controles:**
- Verificar se modo de edição está desativado (F7)
- Verificar configuração de teclas
- Verificar se corrida foi iniciada

**Câmera tremula:**
- Reduzir velocidade de interpolação
- Verificar se `dt` está sendo calculado corretamente
- Ajustar limites de zoom

**Performance baixa:**
- Reduzir FPS máximo nas configurações
- Desativar efeitos visuais
- Reduzir resolução

### Debug

- **F1** - Ativar/desativar debug da IA
- **H** - Alternar HUD completo

### Controles de Carro

- **Jogador 1:** WASD + Shift (turbo) + Espaço (drift)
- **Jogador 2:** Setas + Ctrl (turbo) + Shift (drift)

---

## Controles Completos

### Menu Principal
- **Setas/WASD** - Navegar entre opções
- **ENTER/ESPAÇO** - Selecionar opção
- **ESC** - Sair do jogo
- **M** - Próxima música
- **N** - Música anterior

### Durante o Jogo
- **ESC** - Pausar/despausar (modo normal) ou voltar ao menu (após vitória)
- **H** - Alternar HUD completo
- **F1** - Ativar/desativar debug da IA

### Controles de Carro
- **Jogador 1:**
  - **WASD** - Movimento (acelerar, direita, esquerda, frear)
  - **Shift** - Turbo
  - **Espaço** - Drift (por clique)
- **Jogador 2:**
  - **Setas** - Movimento (acelerar, direita, esquerda, frear)
  - **Ctrl** - Turbo
  - **Shift** - Drift (hold)

### Controles de Música
- **M** - Próxima música
- **N** - Música anterior

### Editor de Checkpoints
- **F7** - Ativar/desativar modo edição
- **F5** - Salvar checkpoints
- **F6** - Carregar checkpoints
- **F8** - Limpar todos os checkpoints
- **F9** - Próximo mapa (placeholder)
- **F10** - Mostrar todos os checkpoints
- **F12** - Mostrar rota (placeholder)
- **Clique em checkpoint** - Selecionar/mover checkpoint
- **Ctrl+Clique** - Adicionar novo checkpoint
- **Arrastar área vazia** - Mover câmera
- **DEL** - Remover checkpoint selecionado

---

**Versão:** 2.0  
**Última atualização:** Dezembro 2024
