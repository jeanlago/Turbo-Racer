# 🎨 Personalização - Turbo Racer

Guia para personalizar e modificar o Turbo Racer.

## 📋 Áreas de Personalização

### 1. Configurações de Jogo
### 2. Interface e HUD
### 3. Física e Controles
### 4. Áudio e Música
### 5. Gráficos e Efeitos

---

## ⚙️ Configurações de Jogo

### Arquivo `config.json`

```json
{
  "audio": {
    "volume_master": 1.0,
    "volume_musica": 0.8,
    "volume_efeitos": 0.9,
    "audio_habilitado": true,
    "musica_habilitada": true,
    "musica_no_menu": true,
    "musica_no_jogo": true,
    "musica_aleatoria": false
  },
  "video": {
    "resolucao": [1280, 720],
    "fullscreen": false,
    "tela_cheia_sem_bordas": false,
    "vsync": true,
    "fps_max": 60,
    "qualidade_alta": true
  },
  "controles": {
    "sensibilidade_volante": 1.0,
    "inverter_volante": false,
    "auto_centro": true
  },
  "jogo": {
    "dificuldade_IA": 1.0,
    "modo_drift": true,
    "mostrar_fps": false,
    "mostrar_debug": false
  }
}
```

### Modificações Comuns

**Alterar Resolução:**
```json
"resolucao": [1920, 1080]
```

**Ativar Tela Cheia:**
```json
"fullscreen": true
```

**Ajustar Volume:**
```json
"volume_musica": 0.5
```

---

## 🎨 Interface e HUD

### Personalizar Menus

#### Navegação de Menu
O sistema de menus usa controles intuitivos:
- **Setas ←→ ou A/D:** Navegar entre opções do menu principal
- **Setas ↑↓ ou W/S:** Navegar entre opções verticais (ex: número de jogadores)
- **ENTER ou ESPAÇO:** Confirmar seleção
- **ESC:** Voltar ao menu anterior

#### Modificar Layout de Menu
Para ajustar espaçamentos e posições dos menus:

```python
# Em src/core/menu.py, função modo_jogo_loop()
# Ajustar tamanho da caixa
caixa_largura = 600  # Largura da caixa
caixa_altura = 500   # Altura da caixa

# Ajustar espaçamentos
y = caixa_y + 120 + i * 50  # Espaçamento entre opções (50px)
```

#### Adicionar Novas Opções de Menu
Para adicionar novas opções ao menu de modo de jogo:

```python
# Em src/core/menu.py, função modo_jogo_loop()
opcoes_modo = [
    ("1 JOGADOR", ModoJogo.UM_JOGADOR),
    ("2 JOGADORES", ModoJogo.DOIS_JOGADORES),
    # Adicionar nova opção aqui
    ("NOVA_OPCAO", ModoJogo.NOVA_OPCAO)
]
```

### Personalizar HUD

#### Ativar Elementos Removidos

```python
# Em src/core/hud.py, função desenhar_hud_completo()
def desenhar_hud_completo(self, superficie, carro):
    # ... código existente ...
    
    # Descomente para ativar elementos
    self.desenhar_informacoes_carro(superficie, carro)
    self.desenhar_minimapa(superficie, carro, checkpoints, camera)
    self.desenhar_debug_info(superficie, carro, fps, tempo_jogo)
    self.desenhar_controles(superficie)
```

#### Modificar Posições

```python
# Velocímetro
self.velocimetro_centro = (100, 100)  # Era (100, 100)

# Nitro
self.nitro_centro = (900, 650)  # Era (950, 650)
```

#### Alterar Cores

```python
# Cores do HUD
COR_VELOCIMETRO = (255, 255, 255)  # Branco
COR_NITRO = (0, 200, 255)          # Azul
COR_TEXTO = (255, 255, 255)        # Branco
```

### Personalizar Menus

#### Alterar Cores dos Botões

```python
# Em src/core/menu.py
COR_BOTAO_NORMAL = (255, 255, 255)    # Branco
COR_BOTAO_HOVER = (0, 200, 255)       # Azul
COR_BOTAO_SELECIONADO = (255, 215, 0) # Dourado
```

#### Modificar Fontes

```python
# Tamanhos de fonte
FONTE_TITULO = 48
FONTE_BOTAO = 32
FONTE_TEXTO = 20
```

---

## 🚗 Física e Controles

### Ajustar Física dos Carros

#### Parâmetros Globais

```python
# Em config.py
VEL_MAX = 3.5              # Velocidade máxima
ACEL_BASE = 0.08           # Aceleração base
ATRITO_GERAL = 0.992       # Atrito geral
ATRITO_DERRAPANDO = 0.985  # Atrito durante drift
```

#### Parâmetros por Tipo de Tração

```python
# Em carro_fisica.py
if tipo_tracao == "RWD":
    self.grip_lateral = 0.7   # Menor grip = mais drift
    self.acel_base = 0.08
elif tipo_tracao == "FWD":
    self.grip_lateral = 0.95  # Maior grip = mais estável
    self.acel_base = 0.09
elif tipo_tracao == "AWD":
    self.grip_lateral = 0.8   # Grip médio
    self.acel_base = 0.085
```

### Personalizar Controles

#### Alterar Teclas

```python
# Em main.py, CARROS_DISPONIVEIS
{
    "controles": {
        "acelerar": pygame.K_w,      # Era W
        "frear": pygame.K_s,         # Era S
        "esquerda": pygame.K_a,      # Era A
        "direita": pygame.K_d,       # Era D
        "turbo": pygame.K_LSHIFT     # Era Shift
    }
}
```

#### Adicionar Controles Personalizados

```python
# Controles para jogador 2
controles_p2 = {
    "acelerar": pygame.K_UP,
    "frear": pygame.K_DOWN,
    "esquerda": pygame.K_LEFT,
    "direita": pygame.K_RIGHT,
    "turbo": pygame.K_RCTRL,
    "drift": pygame.K_RSHIFT  # Drift para jogador 2
}
```

---

## 🎵 Áudio e Música

### Adicionar Músicas

#### Estrutura de Arquivos

```
assets/sounds/music/
├── menu_theme.mp3
├── race_theme.mp3
├── drift_theme.mp3
└── victory_theme.mp3
```

#### Configurar no Código

```python
# Em src/core/musica.py
MUSICAS = [
    "assets/sounds/music/menu_theme.mp3",
    "assets/sounds/music/race_theme.mp3",
    "assets/sounds/music/drift_theme.mp3"
]
```

### Adicionar Efeitos Sonoros

```python
# Efeitos sonoros
EFEITOS = {
    "turbo": "assets/sounds/effects/turbo.wav",
    "drift": "assets/sounds/effects/drift.wav",
    "checkpoint": "assets/sounds/effects/checkpoint.wav",
    "vitoria": "assets/sounds/effects/vitoria.wav"
}
```

---

## 🎨 Gráficos e Efeitos

### Personalizar Partículas

```python
# Em src/core/particulas.py
class Particula:
    def __init__(self, x, y, cor=(255, 255, 255)):
        self.x = x
        self.y = y
        self.cor = cor  # Personalizar cor
        self.tamanho = 3  # Personalizar tamanho
        self.vida = 30   # Personalizar duração
```

### Modificar Efeitos Visuais

#### Efeito de Drift

```python
# Cores das partículas de drift
COR_FUMAÇA = (100, 100, 100)  # Cinza
COR_FOGO = (255, 100, 0)      # Laranja
COR_FAÍSCA = (255, 255, 0)    # Amarelo
```

#### Efeito de Turbo

```python
# Efeito visual do turbo
EFEITO_TURBO = {
    "cor": (0, 200, 255),     # Azul
    "intensidade": 0.8,       # Intensidade
    "duracao": 0.9            # Duração em segundos
}
```

---

## 🔧 Modificações Avançadas

### Adicionar Novos Modos de Jogo

```python
# Em src/core/game_modes.py
class TipoJogo(Enum):
    CORRIDA = "corrida"
    DRIFT = "drift"
    TIME_TRIAL = "time_trial"  # Novo modo

# Em main.py
if tipo_jogo == TipoJogo.TIME_TRIAL:
    tempo_limite = 60.0  # 1 minuto
    if tempo_atual >= tempo_limite:
        jogo_terminado = True
```

### Personalizar Sistema de Pontuação

```python
# Em src/core/drift_scoring.py
class DriftScoring:
    def __init__(self):
        self.pontuacao_total = 0
        self.combo_atual = 0
        self.tempo_combo = 0.0
        self.velocidade_minima = 2.0  # Personalizar
        self.angulo_minimo = 15.0     # Personalizar
        self.multiplicador_maximo = 5.0  # Personalizar
```

### Adicionar Novos Tipos de Carro

```python
# Em carro_fisica.py
if tipo_tracao == "HYBRID":
    self.grip_lateral = 0.85
    self.acel_base = 0.09
    self.vel_max = 3.8
    self.consumo_turbo = 0.8  # Menor consumo
```

---

## 📁 Estrutura de Personalização

```
personalizacoes/
├── configs/
│   ├── config_arcade.json
│   ├── config_realista.json
│   └── config_drift.json
├── themes/
│   ├── tema_escuro/
│   ├── tema_claro/
│   └── tema_neon/
└── mods/
    ├── mod_carros_extras/
    ├── mod_mapas_extras/
    └── mod_fisica_realista/
```

---

## ✅ Checklist de Personalização

- [ ] Configurações básicas ajustadas
- [ ] HUD personalizado
- [ ] Controles configurados
- [ ] Física ajustada
- [ ] Áudio personalizado
- [ ] Efeitos visuais modificados
- [ ] Teste de todas as modificações
- [ ] Backup das configurações originais

---

**Próximo:** [API Reference](../API.md)  
**Voltar:** [Guia Principal](../README.md)
