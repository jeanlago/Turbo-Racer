# LISTA DE GAME OBJECTS
## TURBO RACER

---

**Versão:** 2.0  
**Data:** Dezembro 2024  
**Projeto:** Turbo Racer  
**Categoria:** Documentação Técnica  

---

## 1. OBJETOS PRINCIPAIS DO JOGO

### 1.1 **Carro** (`core/carro.py`)
**Tipo:** Entidade Principal  
**Descrição:** Classe principal que representa um veículo no jogo com física realista e sistema de drift.

#### **Propriedades:**
- **Posição:** `x`, `y` (coordenadas no mundo)
- **Orientação:** `angulo` (graus, 0° aponta para -x do sprite)
- **Velocidade:** `vx`, `vy` (velocidades no mundo)
- **Velocidade Longitudinal:** `velocidade` (projeção para HUD)
- **Controles:** `controles` (teclas de controle)
- **Turbo:** `turbo_key` (tecla de turbo)
- **Nome:** `nome` (identificação do carro)

#### **Sistemas Físicos:**
- **Aceleração Base:** 0.08 unidades por frame
- **Velocidade Máxima:** 3.5 unidades por frame
- **Atrito Geral:** 0.992 (redução gradual)
- **Atrito em Drift:** 0.985 (maior perda durante derrapagem)

#### **Sistema de Drift:**
- **Grip Lateral Normal:** 0.82
- **Grip Lateral em Drift:** 0.9985
- **Kick Start:** 0.14 (injeção de velocidade lateral)
- **Feed Contínuo:** 0.70 slip por segundo
- **Yaw por Slip:** 0.90 graus por unidade de velocidade lateral

#### **Sistema de Turbo:**
- **Duração:** 0.9 segundos
- **Cooldown:** 2.5 segundos
- **Multiplicador:** 1.25x velocidade
- **Carga:** Sistema de recarga progressiva

#### **Métodos Principais:**
- `__init__(x, y, prefixo_cor, controles, turbo_key, nome)`
- `atualizar(teclas, superficie_mascara, dt)`
- `desenhar(superficie, camera)`
- `usar_turbo()`
- `iniciar_drift()`
- `parar_drift()`

---

### 1.2 **IASimples** (`core/ia_simples.py`)
**Tipo:** Sistema de Inteligência Artificial  
**Descrição:** Controla carros da IA usando algoritmo Pure Pursuit para navegação suave.

#### **Propriedades:**
- **Checkpoints:** `checkpoints` (lista de pontos de navegação)
- **Nome:** `nome` (identificação da IA)
- **Checkpoint Atual:** `checkpoint_atual` (índice do checkpoint atual)
- **Estado:** `chegou` (se completou a rota)
- **Debug:** `debug` (modo de visualização)

#### **Sistema de Recuperação:**
- **Tempo Travado:** `tempo_travado` (tempo no mesmo checkpoint)
- **Máximo Travado:** `max_tempo_travado` (5.0 segundos)
- **Posição Anterior:** `ultima_posicao` (para detectar travamento)
- **Tentativas:** `tentativas_recuperacao` (máximo 3)

#### **Parâmetros Pure Pursuit:**
- **Wheelbase:** 36.0 (distância entre eixos)
- **Lookahead Distance:** 60-200 (distância de antecipação)
- **Velocidade Mínima/Máxima:** 50-200
- **Ganho de Direção:** 1.0

#### **Métodos Principais:**
- `__init__(checkpoints, nome)`
- `controlar(carro, superficie_mascara, is_on_track, dt)`
- `desenhar_debug(superficie, camera)`
- `_calcular_steering_angle(carro, ponto_alvo)`
- `_encontrar_ponto_lookahead(carro, checkpoints)`

---

### 1.3 **Camera** (`core/camera.py`)
**Tipo:** Sistema de Visualização  
**Descrição:** Gerencia a câmera do jogo com seguimento suave e zoom configurável.

#### **Propriedades:**
- **Dimensões da Tela:** `largura_tela`, `altura_tela`
- **Dimensões do Mundo:** `largura_mundo`, `altura_mundo`
- **Posição:** `cx`, `cy` (centro da câmera)
- **Zoom:** `zoom` (nível de zoom)
- **Alvo:** `alvo` (objeto seguido pela câmera)

#### **Métodos Principais:**
- `__init__(largura_tela, altura_tela, largura_mundo, altura_mundo, zoom)`
- `set_alvo(alvo)`
- `atualizar(dt)`
- `mundo_para_tela(x, y)`
- `tela_para_mundo(x, y)`
- `desenhar_fundo(superficie, imagem)`

---

## 2. SISTEMAS DE GERENCIAMENTO

### 2.1 **GerenciadorCorrida** (`core/corrida.py`)
**Tipo:** Sistema de Gameplay  
**Descrição:** Gerencia o estado da corrida, contagem regressiva, posicionamento e finalização.

#### **Propriedades:**
- **Contagem Regressiva:** `contagem_regressiva` (3.0 segundos)
- **Corrida Iniciada:** `iniciada` (estado da corrida)
- **Progresso por Carro:** `proximo_checkpoint`, `voltas`, `finalizou`
- **Tempo Global:** `tempo_global` (tempo desde o início)
- **Tempo Final:** `tempo_final` (tempo de finalização por carro)

#### **Áreas de Controle:**
- **Linha de Largada:** `ret_largada` (retângulo de detecção)
- **Checkpoints:** `ret_checkpoints` (lista de retângulos)

#### **Métodos Principais:**
- `__init__(fonte)`
- `registrar_carro(carro)`
- `atualizar_contagem(dt)`
- `atualizar_tempo(dt)`
- `pode_controlar()`
- `desenhar_semaforo(tela, largura, altura)`
- `desenhar_hud(tela, carros)`
- `desenhar_podio(tela, largura, altura, carros)`

---

### 2.2 **GerenciadorDrift** (`core/corrida.py`)
**Tipo:** Sistema de Pontuação  
**Descrição:** Gerencia o sistema de pontuação por derrapagem quando o modo drift está ativo.

#### **Propriedades:**
- **Pontos Base:** `DRIFT_PONTOS_BASE` (pontos por drift)
- **Fator de Velocidade:** `DRIFT_PONTOS_VEL_FACTOR` (multiplicador por velocidade)
- **Decay por Segundo:** `DRIFT_DECAY_POR_SEG` (redução de pontos)
- **Combo Máximo:** `DRIFT_COMBO_MAX` (máximo de combo)
- **Step do Combo:** `DRIFT_COMBO_STEP` (incremento do combo)

#### **Métodos Principais:**
- `__init__(fonte)`
- `atualizar(carro, dt)`
- `desenhar_hud(tela, x, y)`

---

### 2.3 **CheckpointManager** (`core/checkpoint_manager.py`)
**Tipo:** Sistema de Edição  
**Descrição:** Gerencia a criação, edição e salvamento de checkpoints para navegação da IA.

#### **Propriedades:**
- **Checkpoints:** `checkpoints` (lista de coordenadas)
- **Modo Edição:** `modo_edicao` (estado do editor)
- **Checkpoint Selecionado:** `checkpoint_selecionado` (índice selecionado)
- **Checkpoint em Arrastar:** `checkpoint_em_arraste` (índice sendo movido)
- **Mapa Atual:** `mapa_atual` (mapa sendo editado)

#### **Métodos Principais:**
- `__init__(mapa_atual)`
- `adicionar_checkpoint(x, y)`
- `remover_checkpoint(indice)`
- `mover_checkpoint(indice, novo_x, novo_y)`
- `trocar_mapa(novo_mapa)`
- `processar_clique(x, y, camera)`
- `desenhar(superficie, camera)`
- `salvar_checkpoints()`
- `carregar_checkpoints()`

---

## 3. SISTEMAS DE ÁUDIO E INTERFACE

### 3.1 **GerenciadorMusica** (`core/musica.py`)
**Tipo:** Sistema de Áudio  
**Descrição:** Gerencia a reprodução de música, controle de volume e seleção de faixas.

#### **Propriedades:**
- **Músicas:** `musicas` (lista de faixas disponíveis)
- **Música Atual:** `musica_atual` (índice da música tocando)
- **Volume:** `volume` (nível de volume)
- **Estados:** `musica_habilitada`, `musica_no_menu`, `musica_no_jogo`
- **Tocando:** `musica_tocando` (estado de reprodução)
- **Nome Atual:** `nome_musica_atual` (nome da música)

#### **Métodos Principais:**
- `__init__()`
- `carregar_musicas()`
- `tocar_musica(indice)`
- `parar_musica()`
- `proxima_musica()`
- `musica_aleatoria()`
- `definir_volume(volume)`
- `verificar_fim_musica()`
- `obter_nome_musica_atual()`

---

### 3.2 **PopupMusica** (`core/popup_musica.py`)
**Tipo:** Interface de Usuário  
**Descrição:** Exibe popup visual com informações da música atual e controles.

#### **Propriedades:**
- **Ativo:** `ativo` (se o popup está visível)
- **Tempo Visível:** `tempo_visivel` (duração da exibição)
- **Nome da Música:** `nome_musica` (nome exibido)
- **Posição:** `posicao_x` (posição horizontal)
- **Alpha:** `alpha` (transparência)
- **Disco:** `disco_original` (sprite do disco de vinil)

#### **Estados de Animação:**
- **Texto Offset:** `texto_offset` (posição do texto)
- **Tempo do Texto:** `texto_tempo` (tempo de animação)
- **Estado do Texto:** `texto_estado` (pausa, deslizando, etc.)
- **Terminou Deslizar:** `texto_terminou_deslizar` (flag de animação)

#### **Métodos Principais:**
- `__init__()`
- `carregar_disco()`
- `criar_disco_simples()`
- `mostrar(nome_musica)`
- `esconder()`
- `atualizar(dt)`
- `desenhar(superficie)`
- `verificar_hover(mouse_x, mouse_y)`

---

## 4. SISTEMAS DE EFEITOS VISUAIS

### 4.1 **Particula** (`core/particulas.py`)
**Tipo:** Efeito Visual  
**Descrição:** Representa uma partícula individual no sistema de efeitos.

#### **Propriedades:**
- **Posição:** `x`, `y` (coordenadas)
- **Velocidade:** `vx`, `vy` (velocidades)
- **Vida:** `life` (duração da partícula)
- **Tempo:** `t` (tempo decorrido)
- **Ângulo:** `ang` (rotação)
- **Escalas:** `scale0`, `scale1` (escala inicial e final)
- **Alphas:** `alpha0`, `alpha1` (transparência inicial e final)

#### **Métodos Principais:**
- `__init__(x, y, vx, vy, life, ang, scale0, scale1, alpha0, alpha1)`
- `alive()` (verifica se está viva)
- `update(dt)` (atualiza posição e tempo)
- `interp()` (interpola escala e alpha)

---

### 4.2 **EmissorFumaca** (`core/particulas.py`)
**Tipo:** Sistema de Partículas  
**Descrição:** Gerencia a emissão de partículas de fumaça durante drift.

#### **Propriedades:**
- **Textura:** `tex` (imagem da partícula)
- **Partículas:** `ps` (lista de partículas ativas)
- **Acumulador:** `_accum` (controle de taxa de emissão)

#### **Métodos Principais:**
- `__init__()`
- `spawn(x, y, dirx, diry, taxa_qps, dt)`
- `update(dt)`
- `draw(surface, camera)`

---

## 5. SISTEMAS DE MENU E INTERFACE

### 5.1 **Escolha** (`core/menu.py`)
**Tipo:** Enumeração  
**Descrição:** Define as opções disponíveis no menu principal.

#### **Valores:**
- `JOGAR = 0`
- `SELECIONAR_CARROS = 1`
- `SELECIONAR_MAPAS = 2`
- `OPCOES = 3`
- `SAIR = 4`

---

### 5.2 **Sistema de Menus** (`core/menu.py`)
**Tipo:** Interface de Usuário  
**Descrição:** Gerencia todos os menus do jogo (principal, seleção, opções).

#### **Funções Principais:**
- `menu_loop(screen)` - Loop do menu principal
- `selecionar_carros_loop(screen)` - Seleção de veículos
- `selecionar_mapas_loop(screen)` - Seleção de mapas
- `opcoes_loop(screen)` - Configurações do jogo
- `run()` - Função principal do sistema de menus

#### **Categorias de Opções:**
- **AUDIO:** Volume, música, efeitos
- **VIDEO:** Resolução, fullscreen, qualidade
- **CONTROLES:** Sensibilidade, inversão, auto centro
- **JOGO:** Dificuldade IA, modo drift, debug

---

## 6. SISTEMAS DE DETECÇÃO E FÍSICA

### 6.1 **Sistema de Pista** (`core/pista.py`)
**Tipo:** Sistema de Detecção  
**Descrição:** Gerencia a detecção de pista, colisões e navegação.

#### **Funções Principais:**
- `carregar_pista()` - Carrega mapa e cria máscaras
- `eh_pixel_da_pista(surface, x, y)` - Verifica se pixel é pista
- `eh_pixel_transitavel(surface, x, y)` - Verifica se pixel é transitável
- `extrair_checkpoints(surface)` - Extrai checkpoints da imagem
- `calcular_posicoes_iniciais(mask_guias)` - Calcula posições iniciais

#### **Cores Reconhecidas:**
- **Verde (0, 255, 0):** Limite da pista (não transitável)
- **Laranja (255, 165, 0):** Pista válida (transitável)
- **Magenta (255, 0, 255):** Checkpoints/área transitável

---

## 7. OBJETOS DE CONFIGURAÇÃO

### 7.1 **Configurações Globais** (`config.py`)
**Tipo:** Sistema de Configuração  
**Descrição:** Centraliza todas as configurações do jogo.

#### **Seções Principais:**
- **Caminhos:** Diretórios de assets
- **Sistema de Mapas:** Configuração de múltiplos mapas
- **Física:** Parâmetros de movimento e colisão
- **IA:** Configurações do algoritmo Pure Pursuit
- **Áudio:** Configurações de som e música

#### **Funções Utilitárias:**
- `obter_caminho_mapa()` - Retorna caminho do mapa atual
- `obter_caminho_guias()` - Retorna caminho das guias
- `obter_caminho_checkpoints()` - Retorna caminho dos checkpoints
- `carregar_configuracoes()` - Carrega configurações do JSON
- `salvar_configuracoes()` - Salva configurações no JSON

---

## 8. OBJETOS DE DADOS

### 8.1 **Carros Disponíveis** (`main.py`)
**Tipo:** Dados de Configuração  
**Descrição:** Lista de carros configurados no jogo.

#### **Estrutura:**
```python
CARROS_DISPONIVEIS = [
    {
        "nome": "Mustang",
        "prefixo_cor": "Car1",
        "posicao": (570, 145),
        "sprite_selecao": "Car1"
    },
    # ... mais carros
]
```

#### **Propriedades por Carro:**
- **Nome:** Nome exibido na interface
- **Prefixo Cor:** Prefixo do arquivo de sprite
- **Posição:** Posição na tela de seleção
- **Sprite Seleção:** Nome do sprite de seleção

---

### 8.2 **Mapas Disponíveis** (`config.py`)
**Tipo:** Dados de Configuração  
**Descrição:** Configuração de mapas disponíveis no jogo.

#### **Estrutura:**
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

---

## 9. HIERARQUIA DE OBJETOS

### 9.1 **Estrutura Hierárquica:**
```
Turbo Racer
├── Sistema de Menus
│   ├── Menu Principal
│   ├── Seleção de Carros
│   ├── Seleção de Mapas
│   └── Opções
├── Sistema de Jogo
│   ├── GerenciadorCorrida
│   ├── GerenciadorDrift
│   └── CheckpointManager
├── Entidades
│   ├── Carro (Player 1)
│   ├── Carro (Player 2)
│   └── Carro (IA)
├── Sistemas de IA
│   ├── IASimples (Carro 2)
│   └── IASimples (Carro 3)
├── Sistemas Visuais
│   ├── Camera
│   ├── Sistema de Partículas
│   └── PopupMusica
├── Sistemas de Áudio
│   └── GerenciadorMusica
└── Sistemas de Detecção
    └── Sistema de Pista
```

---

## 10. CICLO DE VIDA DOS OBJETOS

### 10.1 **Inicialização:**
1. **Configurações** são carregadas
2. **Assets** são carregados (sprites, músicas, mapas)
3. **Sistemas** são inicializados (áudio, física, IA)
4. **Entidades** são criadas (carros, câmera)
5. **Interface** é configurada (menus, HUD)

### 10.2 **Loop Principal:**
1. **Input** é processado
2. **Física** é atualizada
3. **IA** calcula movimentos
4. **Sistemas** são atualizados
5. **Renderização** é executada

### 10.3 **Finalização:**
1. **Dados** são salvos
2. **Recursos** são liberados
3. **Sistemas** são finalizados

---

## 11. RELACIONAMENTOS ENTRE OBJETOS

### 11.1 **Dependências Principais:**
- **Carro** → **Sistema de Pista** (detecção de colisão)
- **Carro** → **Sistema de Partículas** (efeitos de drift)
- **IA** → **CheckpointManager** (navegação)
- **Camera** → **Carro** (seguimento)
- **GerenciadorCorrida** → **Carro** (gerenciamento)

### 11.2 **Comunicação:**
- **Eventos** entre sistemas
- **Callbacks** para atualizações
- **Referências** diretas para acesso rápido
- **Configurações** compartilhadas

---

## 12. OTIMIZAÇÕES E PERFORMANCE

### 12.1 **Otimizações Implementadas:**
- **Slots** em classes de partículas
- **Pooling** de objetos reutilizáveis
- **Culling** de objetos fora da tela
- **Lazy Loading** de assets
- **Delta Time** para frame rate independente

### 12.2 **Métricas de Performance:**
- **FPS Target:** 60-120 FPS
- **Memória:** Otimizada para partículas
- **CPU:** Algoritmos eficientes de IA
- **GPU:** Renderização otimizada

---

**Documento elaborado por:** JeanM  
**Data de criação:** Dezembro 2024  
**Versão do documento:** 2.0  
**Status:** Finalizado
