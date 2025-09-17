# 📚 Documentação Técnica - Turbo Racer

## Índice
1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Módulos Principais](#módulos-principais)
4. [Sistema de Mapas](#sistema-de-mapas)
5. [Sistema de IA](#sistema-de-ia)
6. [Física do Jogo](#física-do-jogo)
7. [Sistema de Checkpoints](#sistema-de-checkpoints)
8. [Interface e Menus](#interface-e-menus)
9. [Sistema de Áudio](#sistema-de-áudio)
10. [Configurações](#configurações)
11. [API Reference](#api-reference)
12. [Exemplos de Uso](#exemplos-de-uso)

---

## Visão Geral

O Turbo Racer é um jogo de corrida 2D desenvolvido em Python com Pygame, focado em:
- **Física realista** de veículos com derrapagem e colisões
- **IA inteligente** usando algoritmo Pure Pursuit
- **Sistema escalável** de múltiplos mapas
- **Editor visual** de checkpoints
- **Interface modular** e configurável

### Tecnologias Utilizadas
- **Python 3.10+**
- **Pygame** - Renderização e input
- **JSON** - Configurações e dados
- **Algoritmo Pure Pursuit** - Navegação da IA

---

## Arquitetura do Sistema

### Estrutura Modular
```
src/
├── main.py                 # Ponto de entrada e loop principal
├── config.py              # Configurações globais
└── core/
    ├── carro.py           # Física e controle dos veículos
    ├── pista.py           # Detecção de pista e colisões
    ├── camera.py          # Sistema de câmera
    ├── corrida.py         # Gerenciamento de corrida
    ├── ia_simples.py      # Inteligência artificial
    ├── checkpoint_manager.py # Editor de checkpoints
    ├── menu.py            # Sistema de menus
    ├── musica.py          # Gerenciador de áudio
    ├── particulas.py      # Efeitos visuais
    └── popup_musica.py    # Interface de música
```

### Fluxo de Execução
1. **Inicialização** - Carregamento de configurações e assets
2. **Menu Principal** - Seleção de opções e configurações
3. **Seleção de Carros/Mapas** - Escolha de veículos e pistas
4. **Loop de Jogo** - Física, IA, renderização e input
5. **Finalização** - Salvamento de dados e retorno ao menu

---

## Módulos Principais

### `main.py` - Loop Principal
**Responsabilidade:** Coordenação geral do jogo e loop principal

**Funções Principais:**
- `principal(carro_selecionado_p1, carro_selecionado_p2, mapa_selecionado)` - Função principal do jogo
- `is_on_track(x, y)` - Verifica se posição é transitável

**Variáveis Importantes:**
- `CARROS_DISPONIVEIS` - Lista de carros configurados
- `arrastando_checkpoint` - Estado do drag & drop
- `checkpoint_em_arraste` - Checkpoint sendo movido

### `config.py` - Configurações Globais
**Responsabilidade:** Centralização de todas as configurações

**Seções Principais:**
- **Caminhos** - Diretórios de assets
- **Sistema de Mapas** - Configuração de múltiplos mapas
- **Física** - Parâmetros de movimento e colisão
- **IA** - Configurações do algoritmo Pure Pursuit
- **Áudio** - Configurações de som e música

**Funções Utilitárias:**
- `obter_caminho_mapa()` - Retorna caminho do mapa atual
- `obter_caminho_guias()` - Retorna caminho das guias
- `obter_caminho_checkpoints()` - Retorna caminho dos checkpoints
- `carregar_configuracoes()` - Carrega configurações do JSON
- `salvar_configuracoes()` - Salva configurações no JSON

---

## Sistema de Mapas

### Estrutura de Dados
```python
MAPAS_DISPONIVEIS = {
    "Map_1": {
        "nome": "Pista Principal",
        "arquivo_mapa": "path/to/map.png",
        "arquivo_guias": "path/to/guides.png", 
        "arquivo_checkpoints": "path/to/checkpoints.json",
        "waypoints_fallback": [(x1, y1), (x2, y2), ...]
    }
}
```

### Adicionando Novos Mapas
1. **Preparar Assets:**
   - Mapa principal: `Mapa_Nome.png`
   - Guias: `guides/Mapa_Nome_guides.png`
   - Checkpoints: `guides/Mapa_Nome_checkpoints.json` (criado automaticamente)

2. **Configurar no config.py:**
   ```python
   "Mapa_Nome": {
       "nome": "Nome Exibido",
       "arquivo_mapa": os.path.join(DIR_MAPS, "Mapa_Nome.png"),
       "arquivo_guias": os.path.join(DIR_MAPS_GUIDES, "Mapa_Nome_guides.png"),
       "arquivo_checkpoints": os.path.join(DIR_MAPS_GUIDES, "Mapa_Nome_checkpoints.json"),
       "waypoints_fallback": [(x1, y1), (x2, y2), ...]
   }
   ```

3. **Criar Checkpoints:**
   - Ativar modo edição (F7)
   - Posicionar checkpoints visualmente
   - Salvar (F5)

### Detecção de Pista (`pista.py`)
**Funções Principais:**
- `eh_pixel_da_pista(surface, x, y)` - Verifica se pixel é pista válida
- `eh_pixel_transitavel(surface, x, y)` - Verifica se pixel é transitável
- `carregar_pista()` - Carrega mapa e cria máscaras
- `extrair_checkpoints(surface)` - Extrai checkpoints da imagem

**Cores Reconhecidas:**
- **Verde (0, 255, 0)** - Limite da pista (não transitável)
- **Laranja (255, 165, 0)** - Pista válida
- **Magenta (255, 0, 255)** - Checkpoints/área transitável

---

## Sistema de IA

### Algoritmo Pure Pursuit (`ia_simples.py`)
**Classe:** `IASimples`

**Parâmetros Configuráveis:**
- `PP_WHEELBASE` - Distância entre eixos (36.0)
- `PP_LD_MIN/MAX` - Lookahead distance (60-200)
- `PP_V_MIN/MAX` - Velocidade mínima/máxima (50-200)
- `PP_STEER_GAIN` - Ganho de direção (1.0)

**Métodos Principais:**
- `controlar(carro, mask_guias, is_on_track, dt)` - Controla o carro
- `desenhar_debug(superficie, camera)` - Desenha debug visual
- `_calcular_steering_angle()` - Calcula ângulo de direção
- `_encontrar_ponto_lookahead()` - Encontra próximo ponto alvo

**Estados da IA:**
- **Normal** - Seguindo checkpoints
- **Stuck** - Preso, tentando recuperar
- **Recover** - Recuperando de situação presa

### Navegação
1. **Busca próximo checkpoint** na lista
2. **Calcula ponto lookahead** baseado na velocidade
3. **Determina ângulo de direção** usando Pure Pursuit
4. **Aplica aceleração/frenagem** baseada na curvatura
5. **Detecta situações problemáticas** e tenta recuperar

---

## Física do Jogo

### Sistema de Movimento (`carro.py`)
**Classe:** `Carro`

**Componentes Físicos:**
- **Velocidade Longitudinal** - Para frente/trás
- **Velocidade Lateral** - Para esquerda/direita  
- **Atrito** - Redução gradual da velocidade
- **Inércia** - Manutenção do movimento

**Parâmetros Físicos:**
```python
VEL_MAX = 3.5              # Velocidade máxima
ACEL_BASE = 0.08           # Aceleração base
ATRITO_GERAL = 0.992       # Atrito geral
ATRITO_DERRAPANDO = 0.985  # Atrito durante drift
```

**Sistema de Drift:**
- **Ativação** - Espaço (P1) ou Shift (P2)
- **Pontuação** - Baseada em velocidade e ângulo
- **Efeitos Visuais** - Partículas de fumaça
- **Decay** - Pontos diminuem com o tempo

**Sistema de Turbo:**
- **Ativação** - Shift (P1) ou Ctrl (P2)
- **Duração** - 0.9 segundos
- **Cooldown** - 2.5 segundos
- **Multiplicador** - 1.25x velocidade

### Detecção de Colisões
**Método:** Amostragem de pontos ao redor do carro
```python
amostras_local = [(0, 0), (10, 0), (-10, 0), (0, 6), (0, -6)]
```

**Resposta à Colisão:**
- **Rebote** - Velocidade invertida com redução
- **Posição** - Retorna à posição anterior
- **Velocidade Mínima** - Mantém velocidade mínima de ré

---

## Sistema de Checkpoints

### Editor Visual (`checkpoint_manager.py`)
**Classe:** `CheckpointManager`

**Funcionalidades:**
- **Adicionar** - Clique em área vazia
- **Mover** - Arrastar e soltar
- **Remover** - Tecla DEL
- **Salvar/Carregar** - F5/F6
- **Trocar Mapas** - F9

**Estados Visuais:**
- **Normal** - Magenta (checkpoint padrão)
- **Selecionado** - Amarelo (checkpoint selecionado)
- **Em Arrastar** - Laranja (checkpoint sendo movido)

**Formato de Dados:**
```json
[
  [541.0, 161.0],
  [203.0, 154.0],
  [157.0, 582.0]
]
```

### Integração com IA
- **Carregamento Automático** - IA usa checkpoints do arquivo
- **Fallback** - Se não há checkpoints, extrai do mapa
- **Atualização Dinâmica** - Mudanças refletem imediatamente na IA

---

## Interface e Menus

### Sistema de Menus (`menu.py`)
**Classes:** `Escolha` (Enum)

**Menus Disponíveis:**
- **Principal** - Jogar, Selecionar Carros, Selecionar Mapas, Opções
- **Seleção de Carros** - Escolha de veículos para P1 e P2
- **Seleção de Mapas** - Escolha de pista
- **Opções** - Configurações de áudio, vídeo e controles

**Navegação:**
- **Setas** - Navegar entre opções
- **ENTER** - Selecionar
- **ESC** - Voltar
- **M** - Alternar música

### HUD do Jogo
**Elementos:**
- **Posições** - Ranking dos carros
- **Tempo** - Cronômetro da corrida
- **Velocidade** - Velocidade atual
- **Drift Score** - Pontuação de derrapagem (modo drift)
- **FPS** - Quadros por segundo (opcional)
- **Debug IA** - Informações da inteligência artificial

---

## Sistema de Áudio

### Gerenciador de Música (`musica.py`)
**Classe:** `GerenciadorMusica`

**Funcionalidades:**
- **Reprodução** - Tocar, pausar, parar
- **Controle de Volume** - Master, música, efeitos
- **Modo Aleatório** - Seleção aleatória de faixas
- **Loop Automático** - Reprodução contínua

**Formatos Suportados:**
- MP3
- WAV
- OGG

### Interface de Música (`popup_musica.py`)
**Funcionalidades:**
- **Popup Visual** - Mostra música atual
- **Controles** - Próxima, anterior, volume
- **Animações** - Transições suaves

---

## Configurações

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
    "dificuldade_ia": 1.0,
    "modo_drift": true,
    "mostrar_fps": false,
    "mostrar_debug": false
  }
}
```

### Carregamento Dinâmico
- **Inicialização** - Carrega configurações padrão
- **Sobrescrita** - Aplica configurações do JSON
- **Persistência** - Salva alterações automaticamente

---

## API Reference

### `Carro` - Classe Principal do Veículo
```python
class Carro:
    def __init__(self, x, y, prefixo_cor, controles, turbo_key=None, nome="")
    def atualizar(self, teclas, superficie_mascara, dt)
    def desenhar(self, superficie, camera=None)
    def usar_turbo(self)
    def iniciar_drift(self)
    def parar_drift(self)
```

### `IASimples` - Inteligência Artificial
```python
class IASimples:
    def __init__(self, checkpoints, nome="IA")
    def controlar(self, carro, mask_guias, is_on_track, dt)
    def desenhar_debug(self, superficie, camera=None)
    def _calcular_steering_angle(self, carro, ponto_alvo)
    def _encontrar_ponto_lookahead(self, carro, checkpoints)
```

### `CheckpointManager` - Editor de Checkpoints
```python
class CheckpointManager:
    def __init__(self, mapa_atual=None)
    def adicionar_checkpoint(self, x, y)
    def remover_checkpoint(self, indice)
    def mover_checkpoint(self, indice, novo_x, novo_y)
    def trocar_mapa(self, novo_mapa)
    def processar_clique(self, x, y, camera=None)
    def desenhar(self, superficie, camera)
```

### `Camera` - Sistema de Câmera
```python
class Camera:
    def __init__(self, largura_tela, altura_tela, largura_mundo, altura_mundo, zoom=1.0)
    def set_alvo(self, alvo)
    def atualizar(self, dt)
    def mundo_para_tela(self, x, y)
    def tela_para_mundo(self, x, y)
    def desenhar_fundo(self, superficie, imagem)
```

---

## Exemplos de Uso

### Adicionando Novo Carro
```python
# 1. Adicionar sprite em assets/images/cars/
# 2. Adicionar sprite de seleção em assets/images/car_selection/
# 3. Configurar em CARROS_DISPONIVEIS
CARROS_DISPONIVEIS.append({
    "nome": "Novo Carro",
    "prefixo_cor": "NovoCarro",
    "posicao": (600, 200),
    "sprite_selecao": "NovoCarro"
})
```

### Criando Checkpoints Programaticamente
```python
checkpoint_manager = CheckpointManager("Map_1")
checkpoint_manager.adicionar_checkpoint(100, 100)
checkpoint_manager.adicionar_checkpoint(200, 200)
checkpoint_manager.salvar_checkpoints()
```

### Configurando Nova Música
```python
# 1. Adicionar arquivo em assets/sounds/music/
# 2. Configurar em gerenciador_musica
gerenciador_musica.adicionar_musica("caminho/para/musica.mp3")
```

### Personalizando Física
```python
# Em config.py
VEL_MAX = 4.0              # Aumentar velocidade máxima
ACEL_BASE = 0.1            # Aumentar aceleração
ATRITO_GERAL = 0.99        # Reduzir atrito
```

---

## Troubleshooting

### Problemas Comuns

**IA não segue checkpoints:**
- Verificar se checkpoints estão salvos (F5)
- Verificar se arquivo JSON existe
- Usar modo debug (F1) para visualizar

**Carro não responde aos controles:**
- Verificar se modo de edição está desativado (F7)
- Verificar configuração de teclas
- Verificar se corrida foi iniciada

**Música não toca:**
- Verificar se áudio está habilitado
- Verificar volume das configurações
- Verificar se arquivos de música existem

**Performance baixa:**
- Reduzir FPS máximo nas configurações
- Desativar efeitos visuais
- Reduzir resolução

### Debug
- **F1** - Ativar/desativar debug da IA
- **F2** - Ativar/desativar debug da rota
- **F3** - Gravar waypoints
- **F11** - Mostrar FPS

---

## Contribuição

### Estrutura de Commits
```
feat: nova funcionalidade
fix: correção de bug
docs: documentação
style: formatação
refactor: refatoração
test: testes
```

### Padrões de Código
- **Variáveis em português** quando apropriado
- **Comentários mínimos** e essenciais
- **Funções pequenas** e focadas
- **Configurações centralizadas** em config.py

### Testes
- Testar em diferentes resoluções
- Testar com diferentes mapas
- Testar sistema de checkpoints
- Testar performance

---

**Documentação atualizada em:** Dezembro 2024  
**Versão:** 2.0  
**Autor:** Sistema de Desenvolvimento Turbo Racer
