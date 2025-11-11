# Turbo Racer

Um jogo de corrida arcade 2D top-down desenvolvido em **Python** com **Pygame**, oferecendo física realista, múltiplos modos de jogo, IA inteligente e sistema escalável de mapas e carros.

---

## Funcionalidades Principais

-  **Múltiplos Modos de Jogo** - 1 jogador, 2 jogadores (split-screen) e modo drift
-  **Menu de Pausa Completo** - Sistema de pausa com opções de continuar, reiniciar e voltar
-  **Sistema de Economia** - Sistema de dinheiro para desbloquear carros
-  **Sistema de Troféus** - Troféus baseados em posição ou pontuação de drift
-  **Tela de Fim de Jogo** - Popup sobre o jogo com resultados e opções
-  **Sistema de Física Avançado** - 3 tipos de tração (RWD, FWD, AWD) com comportamento único
-  **IA Inteligente** - Algoritmo Pure Pursuit para navegação suave e realista
-  **Sistema de Dificuldade Universal** - 3 níveis (Fácil, Médio, Difícil) para corrida e drift
-  **Sistema de Mapas Escalável** - Detecção automática de mapas sem configuração manual
-  **Editor Visual de Checkpoints** - Crie e edite checkpoints arrastando e soltando
-  **Sistema de Áudio Completo** - Múltiplas faixas musicais com controles independentes
-  **Modo Drift** - Sistema de pontuação automática baseado em derrapagem real com tempo limitado e combos
-  **HUD Dinâmico** - Interface adaptativa com câmera inteligente
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
│  └─ *.json                      # Checkpoints e dados de mapas
├─ src/                           # Código fonte
│  ├─ main.py                     # Ponto de entrada principal
│  ├─ config.py                   # Configurações e constantes
│  └─ core/                       # Módulos principais
│     ├─ carro_fisica.py          # Sistema de física avançada
│     ├─ pista.py                 # Carregamento e detecção de pista
│     ├─ camera.py                # Sistema de câmera dinâmica
│     ├─ corrida.py               # Gerenciador de corrida
│     ├─ ia.py                    # Inteligência artificial (Pure Pursuit)
│     ├─ checkpoint_manager.py    # Editor visual de checkpoints
│     ├─ menu.py                  # Sistema de menus
│     ├─ hud.py                   # Interface de jogo
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
- **Setas ←→ ou A/D** - Navegar entre opções do menu principal
- **Setas ↑↓ ou W/S** - Navegar entre opções verticais (ex: número de jogadores)
- **ENTER ou ESPAÇO** - Confirmar seleção
- **ESC** - Voltar ao menu anterior
- **R** - Recarregar mapas (na seleção de mapas)

### **Editor de Checkpoints**
- **F7** - Ativar/desativar modo edição
- **F5** - Salvar checkpoints
- **F6** - Carregar checkpoints
- **F8** - Limpar todos os checkpoints
- **F10** - Mostrar todos os checkpoints
- **Clique em checkpoint** - Selecionar/mover checkpoint
- **Ctrl+Clique** - Adicionar novo checkpoint
- **Arrastar área vazia** - Mover câmera
- **DEL** - Remover checkpoint selecionado

---

## Como Executar

### **Requisitos**
- **Python 3.10+** (recomendado 3.11+)
- **Pygame 2.5+** - Biblioteca de jogos
- **Windows 10+** (testado) / Linux / macOS

### **⚙️ Instalação**

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

##  Sistema de Mapas Escalável

### ** Adicionar Novo Mapa (AUTOMÁTICO)**

#### **1. Preparar Assets**
```
assets/images/maps/
├── MeuMapa.png                    # OBRIGATÓRIO
└── guides/
    ├── MeuMapa_guides.png         # OPCIONAL
    └── MeuMapa_checkpoints.json   # OPCIONAL (criado automaticamente)
```

#### **2. Ativar o Mapa**
1. **Execute** o jogo
2. **Vá para "Selecionar Mapas"**
3. **Pressione R** para recarregar mapas (se necessário)
4. **Selecione** o novo mapa na lista

#### **3. Criar Checkpoints (Opcional)**
1. **Entre** no mapa
2. **Pressione F7** para modo edição
3. **Posicione** checkpoints clicando na pista
4. **Mova** checkpoints arrastando
5. **Salve** com F5

### **Recursos do Sistema Escalável**

- **Detecção automática** - Mapas aparecem automaticamente
- **Nomes inteligentes** - "MeuMapa" vira "Meu Mapa"
- **Recarregamento dinâmico** - Adicione mapas sem reiniciar
- **Fallback robusto** - Funciona mesmo sem guias/checkpoints
- **Zero configuração** - Apenas coloque os arquivos

### **Especificações de Mapas**

#### **Cores Padrão**
- **Laranja (255, 165, 0)** - Pista transitável
- **Verde (0, 255, 0)** - Limites não transitáveis
- **Magenta (255, 0, 255)** - Checkpoints/área transitável
- **Amarelo (255, 255, 0)** - Linha de largada (guias)

#### **Resolução Recomendada**
- **Mínimo:** 1280x720
- **Recomendado:** 1920x1080
- **Máximo:** 2560x1440 (para performance)

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

### **Sistema de IA**
- **Algoritmo Pure Pursuit** - Navegação suave e realista
- **Detecção Inteligente** - Evita obstáculos e recupera de situações problemáticas
- **Parâmetros Configuráveis** - Wheelbase, lookahead distance, velocidades

### **Sistema de Dificuldade**
- **Modo Corrida** - Ajusta comportamento da IA (Fácil: conservadora, Médio: equilibrada, Difícil: agressiva)
- **Modo Drift** - Ajusta tempo disponível (Fácil: 1:30, Médio: 1:00, Difícil: 0:30)
- **Seleção Intuitiva** - Escolha no submenu "JOGAR" para 1 jogador
- **Feedback Visual** - Exibição da dificuldade atual no HUD

### **Sistema de Pontuação de Drift**
- **Pontuação Automática** - Baseada em derrapagem real (marcas de pneu), não em teclas
- **Sistema de Combo** - Multiplicadores progressivos (x1, x1.5, x2, x3, x5)
- **Tolerância Inteligente** - 3 segundos para manter combo sem derrapagem
- **Parâmetros Sensíveis** - Velocidade mínima 8 km/h, ângulo mínimo 2°
- **Taxa Generosa** - 80 pontos/segundo no nível base
- **Debug Visual** - Ative com F1 para ver o comportamento da IA

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
- **Tempo Limitado** - 2 minutos para acumular pontos
- **Sistema de Combo** - Multiplicador por derrapagens consecutivas
- **Pontuação Inteligente** - Baseada em velocidade e ângulo de derrapagem
- **Efeitos Visuais** - Fumaça e partículas durante o drift
- **Decay Automático** - Pontos diminuem se não houver drift contínuo

### **Sistema de Performance**
- **100+ FPS** - Otimizações agressivas mantendo qualidade visual
- **Marcas de Pneu em 4 Rodas** - Skidmarks completos durante drift
- **Câmera Dinâmica** - Zoom adaptativo baseado na velocidade para sensação de aceleração
- **Renderização Otimizada** - HUD suave sem flickering
- **Sistema de Partículas Inteligente** - Controle de densidade para melhor performance

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
5. **Teste** física e comportamento

### **Adicionando Novos Mapas**
1. **Coloque** o arquivo PNG em `assets/images/maps/`
2. **Execute** o jogo - detecção automática
3. **Use** o editor visual (F7) para checkpoints
4. **Teste** navegação da IA

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
- ** Novos Mapas** - Crie pistas e checkpoints
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

**Desenvolvido com por Jean Marins e Jayson Sales**  
**Versão atual:** 2.5.0  
**Última atualização:** Novembro 2025
