# Turbo Racer

Um jogo de corrida arcade 2D top-down desenvolvido em **Python** com **Pygame**, oferecendo física realista, múltiplos modos de jogo, IA inteligente e sistema escalável de mapas e carros.

---

## Funcionalidades Principais

-  **Múltiplos Modos de Jogo** - 1 jogador, 2 jogadores (split-screen), modo corrida e modo drift
-  **Modo Drift Completo** - Sistema baseado em checkpoints com pontuação dinâmica e multiplicador de voltas
-  **Menu de Pausa Completo** - Sistema de pausa com opções de continuar, reiniciar e voltar
-  **Sistema de Economia** - Sistema de dinheiro para desbloquear carros
-  **Sistema de Troféus** - Troféus baseados em posição (corrida) ou pontuação (drift)
-  **Tela de Fim de Jogo** - Popup sobre o jogo com resultados e opções (separado por jogador no modo 2 jogadores)
-  **Sistema de Física Avançado** - 3 tipos de tração (RWD, FWD, AWD) com comportamento único
-  **IA Inteligente** - Algoritmo Pure Pursuit para navegação suave e realista
-  **Sistema de Dificuldade Universal** - 3 níveis (Fácil, Médio, Difícil) para corrida (IA) e drift (pontuação necessária)
-  **Sistema de Mapas Escalável** - Detecção automática de mapas sem configuração manual
-  **Sistema de Pistas GRIP** - 9 pistas estilo GRIP com tiles dinâmicos e colisão pixel-based
-  **Editor Visual de Checkpoints** - Crie e edite checkpoints arrastando e soltando
-  **Editor de Garagem** - Ajuste posição e tamanho dos carros na oficina visualmente
-  **Sistema de Recordes Separados** - Recordes de corrida (tempo) e drift (pontuação) salvos separadamente
-  **Sistema de Áudio Completo** - Múltiplas faixas musicais com controles independentes
-  **HUD Dinâmico** - Interface adaptativa com posição/voltas ou score/voltas e troféu indicativo
-  **Skidmarks em Todos os Carros** - Marcas de pneu visíveis para jogadores e bots (otimizado)
-  **Performance Otimizada** - 100+ FPS com qualidade visual mantida
-  **Configurações Avançadas** - Resolução, fullscreen, controles e qualidade personalizáveis

---

## Documentação

### **Game Design Document**
- **[game-design.md](docs/design/game-design.md)** - Documento completo de design do jogo
  - Visão geral e conceito principal
  - Mecânicas de jogo detalhadas
  - Sistema de IA e física
  - Arquitetura técnica
  - Roadmap e futuras implementações

### **Documentação Técnica**
- **[API.md](docs/API.md)** - Referência completa da API
  - Classes principais e métodos
  - Sistemas de jogo
  - Configuração e exemplos
  - Troubleshooting

### **Guias de Desenvolvimento**
- **[adding-maps.md](docs/guides/adding-maps.md)** - Como adicionar novos mapas
- **[adding-cars.md](docs/guides/adding-cars.md)** - Como adicionar novos carros
- **[customization.md](docs/guides/customization.md)** - Personalização e modificações

### **Histórico de Versões**
- **[CHANGELOG.md](docs/CHANGELOG.md)** - Histórico completo de mudanças
  - Versão 3.2.1 - Limpeza de código e correção de nomenclatura
  - Versão 3.2.0 - Modo drift reformulado e sistema de pontuação dinâmica
  - Versão 3.1.0 - Sistema GRIP completo e melhorias de IA
  - Versão 3.0.0 - Sistema de pistas GRIP e editor de garagem
  - Versão 2.1.0 - Melhorias de navegação e sistema de mapas
  - Versão 2.0.0 - Modos de jogo e split-screen
  - Versão 1.0.0 - Sistema base

---

## Estrutura do Projeto

```text
Turbo-Racer/
├─ assets/                        # Recursos do jogo
│  ├─ images/
│  │  ├─ cars/                    # Sprites dos carros (12 carros)
│  │  ├─ car_selection/           # Sprites para seleção de carros
│  │  ├─ maps/                    # Mapas do jogo (detecção automática)
│  │  │  └─ guides/               # Guias e checkpoints dos mapas
│  │  ├─ effects/                 # Efeitos visuais (fumaça, nitro, skidmarks)
│  │  ├─ icons/                   # Ícones da interface (velocímetro, nitro)
│  │  └─ ui/                      # Interface do usuário (menus, oficina)
│  └─ sounds/
│     └─ music/                   # Músicas do jogo (6 faixas)
├─ docs/                          # Documentação completa
│  ├─ design/
│  │  └─ game-design.md           # Game Design Document
│  ├─ guides/                     # Guias de desenvolvimento
│  │  ├─ adding-maps.md           # Como adicionar mapas
│  │  ├─ adding-cars.md           # Como adicionar carros
│  │  └─ customization.md         # Personalização
│  ├─ API.md                      # Referência da API
│  └─ CHANGELOG.md                # Histórico de versões
├─ data/                          # Dados e configurações
│  ├─ config.json                 # Configurações do usuário
│  ├─ progresso.json               # Progresso do jogador (dinheiro, carros, recordes, troféus)
│  ├─ garage_config.json           # Configurações da garagem (posições dos carros)
│  └─ *.json                      # Checkpoints e dados de mapas
├─ tools/                         # Ferramentas de desenvolvimento
│  ├─ checkpoint_editor.py        # Editor visual de checkpoints
│  ├─ garage_editor.py            # Editor visual de garagem
│  └─ aplicar_config_garagem.py   # Script para aplicar configurações da garagem
├─ src/                           # Código fonte
│  ├─ main.py                     # Ponto de entrada principal
│  ├─ config.py                   # Configurações e constantes
│  └─ core/                       # Módulos principais
│     ├─ carro_fisica.py          # Sistema de física avançada
│     ├─ camera.py                # Sistema de câmera dinâmica
│     ├─ corrida.py               # Gerenciador de corrida
│     ├─ ia.py                    # Inteligência artificial (Pure Pursuit)
│     ├─ checkpoint_manager.py    # Editor visual de checkpoints
│     ├─ pista_tiles.py           # Sistema de pistas estilo GRIP (tiles dinâmicos)
│     ├─ pista_grip.py            # Colisão pixel-based estilo GRIP
│     ├─ laps_grip.py             # Checkpoints e dados das pistas GRIP
│     ├─ progresso.py             # Gerenciador de progresso (dinheiro, recordes, troféus)
│     ├─ menu.py                  # Sistema de menus
│     ├─ hud.py                   # Interface de jogo (velocímetro, nitro, minimapa, tempos)
│     ├─ musica.py                # Gerenciador de música
│     ├─ particulas.py            # Efeitos de partículas
│     ├─ skidmarks.py             # Sistema de marcas de pneu
│     └─ drift_scoring.py         # Sistema de pontuação de drift
└─ README.md                      # Este arquivo
```

---

## Controles

### **Controles de Carro**

#### **Jogador 1 (Player 1)**
- **W** - Acelerar
- **S** - Frear/Ré
- **A** - Virar Esquerda
- **D** - Virar Direita
- **Shift Esquerdo** - Turbo
- **Espaço** - Drift (por clique)

#### **Jogador 2 (Player 2)**
- **Seta ↑** - Acelerar
- **Seta ↓** - Frear/Ré
- **Seta ←** - Virar Esquerda
- **Seta →** - Virar Direita
- **Ctrl Direito** - Turbo
- **Shift** - Drift (hold)

### **Controles de Música**
- **M** - Próxima música
- **N** - Música anterior

### **Controles Gerais**
- **ESC** - Pausar/despausar ou voltar ao menu
- **H** - Alternar HUD completo
- **F1** - Ativar/desativar debug da IA

### **Menu de Pausa**
- **ESC** - Abrir/fechar menu de pausa
- **↑↓** - Navegar pelas opções
- **ENTER/SPACE** - Selecionar opção
- **Opções disponíveis:**
  - **Continuar** - Retoma o jogo
  - **Reiniciar** - Reinicia a corrida atual
  - **Voltar ao Menu** - Sai do jogo e volta ao menu principal

### **Navegação no Menu**
- **Setas ←→ ou A/D** - Navegar entre opções do menu principal (ordem visual: RECORDES → SELECIONAR CARROS → JOGAR → OPÇÕES → SAIR)
- **Setas ↑↓ ou W/S** - Navegar entre opções verticais (ex: número de jogadores, tipo de jogo)
- **ENTER ou ESPAÇO** - Confirmar seleção
- **ESC** - Voltar ao menu anterior
- **R** - Recarregar mapas (na seleção de mapas)
- **Seleção de Modo de Jogo** - Escolha modo (1/2 jogadores), tipo (Corrida/Drift), voltas (1-3) e dificuldade (Fácil/Médio/Difícil)

### **Editor de Checkpoints**
- **F7** - Ativar/desativar modo edição
- **F5** - Salvar checkpoints (JSON backup)
- **F6** - Carregar checkpoints
- **F8** - Limpar todos os checkpoints
- **F10** - Exportar para `laps_grip.py`
- **R** - Rotacionar checkpoint selecionado (90°)
- **Q/E** - Rotacionar checkpoint selecionado (-15°/+15°)
- **Clique em checkpoint** - Selecionar/mover checkpoint
- **Ctrl+Clique** - Adicionar novo checkpoint
- **Arrastar área vazia** - Mover câmera
- **DEL** - Remover checkpoint selecionado
- **Mouse Wheel** - Zoom in/out

### **Editor de Garagem**
- **F7** - Ativar/desativar modo edição
- **F5** - Salvar configurações em `data/garage_config.json`
- **F6** - Carregar configurações
- **← →** - Navegar entre carros
- **W/A/S/D** - Mover posição (modo edição)
- **Q/E** - Ajustar largura (modo edição)
- **Z/X** - Ajustar altura (modo edição)
- **Mouse** - Arrastar para mover, cantos para redimensionar
- **H** - Mostrar/Ocultar ajuda
- **ESC** - Sair

Veja mais detalhes em: [tools/README_GARAGE_EDITOR.md](tools/README_GARAGE_EDITOR.md)

---

## Como Executar

### **Requisitos**
- **Python 3.10+** (recomendado 3.11+)
- **Pygame 2.5+** - Biblioteca de jogos
- **Windows 10+** (testado) / Linux / macOS

### **Instalação**

#### **Método 1: Instalação Rápida**
```bash
# 1. Instalar Pygame
pip install pygame

# 2. Executar o jogo
python src/main.py
```

#### **Método 2: Instalação com Virtual Environment (Recomendado)**
```bash
# 1. Criar ambiente virtual
python -m venv turbo-racer-env

# 2. Ativar ambiente virtual
# Windows:
turbo-racer-env\Scripts\activate
# Linux/macOS:
source turbo-racer-env/bin/activate

# 3. Instalar dependências
pip install pygame

# 4. Executar o jogo
python src/main.py
```

### **Primeira Execução**
1. **Execute** o jogo pela primeira vez
2. **Configure** as opções em "OPÇÕES" se necessário
3. **Selecione** um carro e mapa
4. **Divirta-se!**

---

## Sistema de Pistas GRIP

O jogo utiliza **exclusivamente** o sistema de pistas GRIP com tiles dinâmicos. O sistema antigo de mapas baseado em imagens PNG foi removido para melhor performance e consistência.

### **Características das Pistas GRIP**

- **9 Pistas Disponíveis** - Pistas numeradas de 1 a 9, cada uma com seu próprio layout de tiles
- **Tiles Dinâmicos** - Pista renderizada dinamicamente baseada na posição do jogador
- **Colisão Pixel-Based** - Detecção baseada em cores dos pixels (estilo GRIP original)
- **Grama Transitável** - Carro pode andar na grama, mas fica mais lento e não ganha pontos de drift
- **Checkpoints Retangulares** - Checkpoints perpendiculares à direção da pista, rotacionáveis
- **Spawn Points** - Múltiplos pontos de spawn configuráveis por pista
- **Minimapas** - Cada pista tem seu próprio minimapa (`track1.png` a `track9.png`)

### **Editor de Checkpoints**

Para editar checkpoints e spawn points de uma pista:

1. **Execute** `python tools/checkpoint_editor.py`
2. **Selecione** a pista (1-9) com **F9** ou setas
3. **Pressione F7** para ativar modo edição
4. **Clique** para adicionar checkpoints
5. **Arraste** para mover checkpoints
6. **R/Q/E** para rotacionar checkpoints selecionados
7. **Shift+F7** para alternar modo spawn points
8. **F10** para exportar para `src/core/laps_grip.py`
9. **F5** para salvar backup em JSON

---

## Configurações

### **Arquivo config.json**
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
    "qualidade_alta": true,
    "mostrar_fps": false
  },
  "controles": {
    "sensibilidade_volante": 1.0,
    "inverter_volante": false,
    "auto_centro": true
  },
  "jogo": {
    "dificuldade_IA": 1.0,
    "modo_drift": true,
    "mostrar_debug": false
  }
}
```

### **Configurações Principais**

#### **Áudio**
- **Volume Master** - Volume geral (0.0 - 1.0)
- **Volume Música** - Volume das músicas (0.0 - 1.0)
- **Volume Efeitos** - Volume dos efeitos sonoros (0.0 - 1.0)
- **Música Aleatória** - Tocar músicas em ordem aleatória

#### **Vídeo**
- **Resolução** - Resolução da tela [largura, altura]
- **Fullscreen** - Modo tela cheia
- **VSync** - Sincronização vertical
- **FPS Máximo** - Limite de FPS (recomendado: 60)
- **Qualidade Alta** - Renderização em alta qualidade

#### **Jogo**
- **Dificuldade IA** - Dificuldade da inteligência artificial (0.5 - 2.0)
- **Modo Drift** - Ativar sistema de drift
- **Mostrar Debug** - Exibir informações de debug

---

## Funcionalidades Avançadas

### **Sistema de Progresso**
- **Dinheiro** - Ganhe dinheiro completando corridas e desbloqueie novos carros
- **Recordes** - Seus melhores tempos são salvos automaticamente por pista
- **Troféus** - Sistema de troféus (Ouro, Prata, Bronze) baseado na posição final
- **Persistência** - Todo progresso é salvo em `data/progresso.json`
- **Menu Recordes** - Visualize seus recordes e troféus conquistados

### **Sistema de IA**
- **Algoritmo Pure Pursuit** - Navegação suave e realista
- **Detecção Inteligente** - Evita obstáculos e recupera de situações problemáticas
- **Parâmetros Configuráveis** - Wheelbase, lookahead distance, velocidades

### **Sistema de Dificuldade**
- **Modo Corrida** - Ajusta comportamento da IA (Fácil: conservadora, Médio: equilibrada, Difícil: agressiva)
- **Modo Drift** - Ajusta pontuação necessária para troféus (Fácil: 60% do médio, Médio: 100%, Difícil: 150%)
- **Disponível em Todos os Modos** - Dificuldade pode ser selecionada em modo 1 e 2 jogadores
- **Seleção Intuitiva** - Escolha no submenu "JOGAR" antes de iniciar
- **Feedback Visual** - Exibição da dificuldade atual no menu

### **Sistema de Pontuação de Drift**
- **Pontuação Automática** - Baseada em derrapagem real (marcas de pneu), não em teclas
- **Sistema de Combo** - Multiplicadores progressivos (x1, x2, x3, x4, x5)
- **Tolerância Inteligente** - 4 segundos para manter combo sem derrapagem
- **Parâmetros Sensíveis** - Velocidade mínima 3 km/h, ângulo mínimo 0.5°
- **Taxa Aumentada** - 2000 pontos/segundo no nível base (aumentado significativamente)
- **Baseado em Checkpoints** - Modo drift termina ao completar todos os checkpoints (não por tempo)
- **Multiplicador de Voltas** - Pontuação alvo multiplicada pelo número de voltas selecionadas
- **Pontuação Alvo Dinâmica** - Baseada no número de checkpoints da pista e dificuldade selecionada
- **Troféu Indicativo** - Troféu ao lado da pontuação indica classificação atual (ouro, prata, bronze)

### **Física Realista**
- **3 Tipos de Tração:**
  - **RWD (Tração Traseira)** - Pode fazer drift, instável em curvas
  - **FWD (Tração Frontal)** - Muito estável, sem drift
  - **AWD (Tração Integral)** - Equilibrado, drift limitado
- **Sistema de Derrapagem** - Baseado em velocidade e ângulo
- **Colisões Realistas** - Rebote e perda de velocidade
- **Turbo com Cooldown** - 0.9s de duração, 2.5s de cooldown

### **Sistema de Áudio**
- **6 Faixas Musicais** - Estilos variados (Cyberpunk, Rock, Rave)
- **Controles Independentes** - Volume master, música e efeitos
- **Modo Aleatório** - Tocar músicas em ordem aleatória
- **Interface Visual** - Controles de música integrados

### **Modo Drift**
- **Baseado em Checkpoints** - Termina ao completar todos os checkpoints (igual ao modo corrida)
- **Sistema de Combo** - Multiplicador por derrapagens consecutivas (x1 a x5)
- **Pontuação Inteligente** - Baseada em velocidade, ângulo e marcas de pneu
- **Multiplicador de Voltas** - Escolha 1, 2 ou 3 voltas - pontuação alvo multiplicada proporcionalmente
- **Pontuação Alvo Dinâmica** - Calculada baseada no número de checkpoints da pista
- **Dificuldade Ajustável** - Fácil (60% do médio), Médio (100%), Difícil (150% do médio)
- **Efeitos Visuais** - Fumaça, partículas e skidmarks durante o drift
- **HUD Unificado** - Mostra pontuação e voltas com troféu indicativo da classificação atual
- **Recordes Separados** - Recordes de drift salvos separadamente dos recordes de corrida

### **Sistema de Performance**
- **100+ FPS** - Otimizações agressivas mantendo qualidade visual
- **Marcas de Pneu em 4 Rodas** - Skidmarks completos durante drift (pretas na pista, marrons na grama)
- **Skidmarks nos Bots** - Bots também deixam marcas de pneu (otimizado para evitar lag)
- **Otimizações de Skidmarks** - Bots criam skidmarks com frequência reduzida e limite menor
- **Câmera Dinâmica** - Zoom adaptativo baseado na velocidade com suavização avançada
- **Renderização Otimizada** - HUD suave sem flickering, cache de sprites otimizado
- **Sistema de Partículas Inteligente** - Controle de densidade para melhor performance
- **Tiles Dinâmicos** - Renderização eficiente de pistas grandes (5000x5000) com tiles
- **Cache de Imagens** - Minimapas e troféus são cacheados para melhor performance
- **Renderização Condicional** - Skidmarks dos bots só são desenhados se estiverem visíveis

### **HUD Completo**
- **Velocímetro** - Mostra velocidade em km/h (até 180 km/h) com oscilação visual no limite
- **Nitro** - Indicador visual de carga do nitro (preenche de baixo para cima)
- **Minimapa** - Mostra posição do jogador, checkpoints e outros carros
- **Modo Corrida** - Exibe posição (1st, 2nd, etc.) e voltas
- **Modo Drift** - Exibe pontuação (sem "Score:") e voltas com troféu indicativo ao lado
- **Tempos** - Exibe tempo total, tempo desde último checkpoint e número de voltas (apenas modo corrida)
- **Aviso Contra Mão** - Alerta visual quando o jogador está indo na direção errada
- **HUD Unificado** - Modo 1 e 2 jogadores usam o mesmo sistema de exibição

---

## Desenvolvimento

### **Arquitetura do Código**
- **Modular** - Cada funcionalidade em seu próprio módulo
- **Escalável** - Fácil adicionar novos mapas e carros
- **Configurável** - Todas as configurações em arquivos JSON
- **Português** - Código e variáveis em português
- **Documentado** - Documentação técnica completa disponível

### **Documentação para Desenvolvedores**
- **[Game Design Document](docs/design/game-design.md)** - Design completo do jogo
- **[API Reference](docs/API.md)** - Referência completa da API
- **[Guias de Desenvolvimento](docs/guides/)** - Como adicionar conteúdo
- **[Changelog](docs/CHANGELOG.md)** - Histórico de mudanças

### **Adicionando Novos Carros**
1. **Adicione** o sprite em `assets/images/cars/`
2. **Configure** em `CARROS_DISPONIVEIS` no `main.py`
3. **Adicione** sprite de seleção em `assets/images/car_selection/`
4. **Defina** tipo de tração (RWD/FWD/AWD)
5. **Use o Editor de Garagem** para ajustar posição e tamanho na oficina
6. **Teste** física e comportamento

### **Adicionando Novos Mapas**
1. **Coloque** o arquivo PNG em `assets/images/maps/`
2. **Execute** o jogo - detecção automática
3. **Use** o editor visual (F7) para checkpoints
4. **Teste** navegação da IA

### **Adicionando Checkpoints em Pistas GRIP**
1. **Execute** `python tools/checkpoint_editor.py`
2. **Selecione** a pista (1-9) com F9
3. **Pressione F7** para ativar modo edição
4. **Clique** para adicionar checkpoints
5. **Arraste** para mover checkpoints
6. **R/Q/E** para rotacionar checkpoints
7. **F10** para exportar para `src/core/laps_grip.py`
8. **F5** para salvar backup em JSON

### **Personalizando Física**
- **Ajuste** constantes em `config.py`
- **Modifique** `core/carro_fisica.py` para física personalizada
- **Configure** parâmetros de IA em `core/ia.py`
- **Teste** diferentes configurações

---

## Contribuição

### **Diretrizes de Contribuição**
- **Siga** a estrutura de código existente
- **Mantenha** a documentação atualizada
- **Teste** suas mudanças antes de submeter
- **Use** commits descritivos com prefixos
- **Consulte** a documentação técnica antes de contribuir

### **Áreas de Contribuição**
- ** Novos Carros** - Adicione sprites e configurações
- ** Novas Pistas GRIP** - Adicione tiles e defina layouts de pistas
- ** Melhorias de IA** - Otimize algoritmos de navegação
- ** Efeitos Visuais** - Adicione partículas e animações
- ** Interface** - Melhore menus e HUD
- ** Documentação** - Melhore guias e referências
- ** Correções** - Reporte e corrija bugs
- ** Performance** - Otimize código e renderização

### **Padrões de Commit**
```
feat: adiciona nova funcionalidade
fix: corrige bug específico
docs: atualiza documentação
style: formatação de código
refactor: refatoração sem mudança de funcionalidade
test: adiciona ou modifica testes
chore: mudanças em build, dependências, etc.
```

---

## Licença

Este projeto é de código aberto e está disponível sob a **licença MIT**.

---

## Suporte

### **Reportar Bugs**
- Use o sistema de [Issues](https://github.com/seu-usuario/turbo-racer/issues) do GitHub
- Inclua informações sobre seu sistema operacional
- Descreva os passos para reproduzir o problema

### **Dúvidas e Ajuda**
- **Documentação:** Consulte a [documentação técnica](docs/API.md)
- **Guias:** Veja os [guias de desenvolvimento](docs/guides/)


### **Sugestões**
- Abra uma [Issue](https://github.com/seu-usuario/turbo-racer/issues) com a tag "enhancement"
- Descreva sua ideia detalhadamente

---



---

**Desenvolvido por Jean Marins e Jayson Sales**  
**Versão atual:** 3.2.1  
**Última atualização:** Novembro 2025

### **Novidades da Versão 3.2.1 (Novembro 2025)**
- **Limpeza de Código** - Removido código não utilizado e comentários desnecessários
- **Nomenclatura Corrigida** - Corrigidos nomes com "IA" no meio de palavras (gerenciador_musica, iniciada, etc.)
- **Código Mais Limpo** - Melhor manutenibilidade e consistência

### **Novidades da Versão 3.2.0 (Novembro 2025)**
- **Modo Drift Reformulado** - Agora baseado em checkpoints ao invés de tempo, termina ao completar todos os checkpoints
- **Sistema de Pontuação Dinâmica** - Pontuação alvo calculada baseada no número de checkpoints da pista e voltas selecionadas
- **Dificuldade no Modo Drift** - Ajusta pontuação necessária para troféus (Fácil: 60%, Médio: 100%, Difícil: 150%)
- **Dificuldade no Modo 2 Jogadores** - Agora é possível escolher dificuldade também no modo 2 jogadores
- **Voltas no Modo Drift** - Escolha 1, 2 ou 3 voltas - pontuação alvo multiplicada proporcionalmente
- **HUD Unificado** - Modo 1 e 2 jogadores usam o mesmo sistema de exibição (posição/voltas ou score/voltas)
- **Troféu Indicativo** - Troféu ao lado da pontuação indica classificação atual no modo drift
- **Recordes Separados** - Recordes de corrida (tempo) e drift (pontuação) salvos separadamente no menu Recordes
- **Fim de Jogo Independente** - No modo 2 jogadores, cada jogador tem seu próprio popup de fim de jogo no lado da tela
- **Jogo Não Congela** - No modo 2 jogadores, quando um jogador termina, o outro continua jogando normalmente
- **Skidmarks nos Bots** - Bots agora deixam marcas de pneu ao derrapar (otimizado para evitar lag)
- **Navegação do Menu Corrigida** - Navegação com A/D ou setas segue a ordem visual correta dos botões
- **Correções de Bugs** - Corrigido bug de pontuação infinita no modo drift e ajustes de pontuação alvo

### **Novidades da Versão 3.0.0**
- Sistema de pistas GRIP (9 pistas com tiles dinâmicos)
- Editor de garagem para ajustar posição e tamanho dos carros
- Sistema de recordes e troféus com persistência
- Minimapa com checkpoints e outros jogadores
- Velocímetro e nitro com indicadores visuais PNG
- Sistema de tempos (total, checkpoint, volta)
- Aviso "Contra Mão" quando jogador vai na direção errada
- Melhorias de performance e otimizações
- Menu de recordes para visualizar conquistas