# GAME DESIGN DOCUMENT (GDD)
## TURBO RACER

---

**Versão:** 2.0  
**Data:** Setembro 2025  
**Desenvolvedor:** Jean Marins e Jayson Sales  
**Gênero:** Corrida Arcade 2D Top-Down  
**Plataforma:** PC (Windows)  
**Motor:** Python + Pygame  

---

## 1. VISÃO GERAL DO JOGO

### 1.1 Conceito Principal
Turbo Racer é um jogo de corrida arcade 2D desenvolvido em Python com Pygame, focado em proporcionar uma experiência de corrida divertida e acessível com física realista, sistema de derrapagem (drift) e inteligência artificial avançada. O jogo combina elementos clássicos de corrida com mecânicas modernas de gameplay.

### 1.2 Proposta de Valor
- **Física Realista**: Sistema de física arcade que simula aceleração, frenagem, derrapagem e colisões
- **IA Inteligente**: Carros controlados por IA usando algoritmo Pure Pursuit para navegação suave
- **Editor Visual**: Sistema completo de criação e edição de checkpoints para personalização de mapas
- **Modularidade**: Arquitetura escalável que permite fácil adição de novos carros, mapas e funcionalidades
- **Acessibilidade**: Controles simples e intuitivos, adequados para jogadores casuais e experientes

### 1.3 Público-Alvo
- **Primário**: Jogadores casuais de 12-35 anos interessados em jogos de corrida
- **Secundário**: Desenvolvedores e modders que desejam personalizar o jogo
- **Terciário**: Estudantes de programação interessados em game development

---

## 2. MECÂNICAS DE JOGO

### 2.1 Sistema de Controle

#### 2.1.1 Controles do Jogador 1
- **Acelerar**: W
- **Frear/Ré**: S
- **Virar Direita**: D
- **Virar Esquerda**: A
- **Turbo**: Shift Esquerdo (hold)
- **Drift**: Espaço (hold)

#### 2.1.2 Controles do Jogador 2
- **Acelerar**: Seta ↑
- **Frear/Ré**: Seta ↓
- **Virar Direita**: Seta →
- **Virar Esquerda**: Seta ←
- **Turbo**: Ctrl Direito (hold)
- **Drift**: Shift (hold)

#### 2.1.3 Controles Gerais
- **M**: Alternar música
- **N**: Próxima música
- **F11**: Alternar modo de tela (Janela/Tela Cheia/Fullscreen)
- **ESC**: Voltar ao menu

### 2.2 Sistema de Física

#### 2.2.1 Movimento Longitudinal
- **Aceleração Base**: 0.08 unidades por frame
- **Velocidade Máxima**: 3.5 unidades por frame
- **Atrito Geral**: 0.992 (redução gradual da velocidade)
- **Atrito em Drift**: 0.985 (maior perda de velocidade durante derrapagem)

#### 2.2.2 Sistema de Drift
- **Ativação**: Hold das teclas de drift (Space/Shift)
- **Grip Lateral Normal**: 0.82 (redução significativa da velocidade lateral)
- **Grip Lateral em Drift**: 0.9985 (permite escorregamento lateral)
- **Kick Start**: 0.14 (fração da velocidade longitudinal injetada em lateral)
- **Feed Contínuo**: 0.70 slip por segundo durante drift
- **Yaw por Slip**: 0.90 graus por unidade de velocidade lateral

#### 2.2.3 Sistema de Turbo
- **Duração**: 0.9 segundos
- **Cooldown**: 2.5 segundos
- **Multiplicador**: 1.25x velocidade
- **Ativação**: Hold das teclas de turbo

### 2.3 Sistema de Colisões
- **Detecção**: Amostragem de 5 pontos ao redor do carro
- **Resposta**: Rebote com redução de velocidade
- **Recuperação**: Retorno à posição anterior válida
- **Velocidade Mínima**: Mantém velocidade mínima de ré para evitar travamento

---

## 3. SISTEMA DE INTELIGÊNCIA ARTIFICIAL

### 3.1 Algoritmo Pure Pursuit
O jogo utiliza o algoritmo Pure Pursuit para controlar os carros da IA, proporcionando navegação suave e realista.

#### 3.1.1 Parâmetros Configuráveis
- **Wheelbase**: 36.0 (distância entre eixos)
- **Lookahead Distance**: 60-200 (distância de antecipação)
- **Velocidade Mínima/Máxima**: 50-200
- **Ganho de Direção**: 1.0

#### 3.1.2 Estados da IA
- **Normal**: Seguindo checkpoints de forma otimizada
- **Stuck**: Detecta quando está preso e tenta recuperação
- **Recover**: Executa manobras de recuperação quando necessário

#### 3.1.3 Sistema de Navegação
1. **Busca Próximo Checkpoint**: Localiza o próximo ponto na sequência
2. **Calcula Ponto Lookahead**: Determina ponto alvo baseado na velocidade
3. **Determina Ângulo de Direção**: Usa Pure Pursuit para calcular direção
4. **Aplica Aceleração/Frenagem**: Baseado na curvatura da rota
5. **Detecta Problemas**: Identifica situações problemáticas e executa recuperação

---

## 4. SISTEMA DE MAPAS E CHECKPOINTS

### 4.1 Estrutura de Mapas
Cada mapa é composto por três elementos principais:
- **Mapa Principal**: Imagem PNG com a pista e obstáculos
- **Mapa de Guias**: Imagem PNG com áreas transitáveis (laranja) e limites (verde)
- **Arquivo de Checkpoints**: JSON com coordenadas dos pontos de navegação

### 4.2 Editor Visual de Checkpoints
Sistema completo de criação e edição de checkpoints:

#### 4.2.1 Funcionalidades
- **Adicionar**: Clique em área vazia para criar novo checkpoint
- **Mover**: Arrastar e soltar para reposicionar
- **Remover**: Tecla DEL para excluir checkpoint selecionado
- **Salvar/Carregar**: F5/F6 para persistir alterações
- **Trocar Mapas**: F9 para alternar entre mapas disponíveis

#### 4.2.2 Estados Visuais
- **Normal**: Magenta (checkpoint padrão)
- **Selecionado**: Amarelo (checkpoint selecionado)
- **Em Arrastar**: Laranja (checkpoint sendo movido)

### 4.3 Sistema de Detecção de Pista
- **Verde (0, 255, 0)**: Limite da pista (não transitável)
- **Laranja (255, 165, 0)**: Pista válida (transitável)
- **Magenta (255, 0, 255)**: Checkpoints/área transitável

---

## 5. SISTEMA DE ÁUDIO

### 5.1 Gerenciador de Música
- **Formatos Suportados**: MP3, WAV, OGG
- **Controles de Volume**: Master, música, efeitos (independentes)
- **Modo Aleatório**: Seleção aleatória de faixas
- **Loop Automático**: Reprodução contínua sem interrupção

### 5.2 Interface de Música
- **Popup Visual**: Mostra música atual e controles
- **Controles**: Próxima, anterior, volume
- **Animações**: Transições suaves entre estados

### 5.3 Faixas Incluídas
- Cyberpunk Gaming Retro by Infraction
- Rave gothic angelcore by infraction
- Rock Sport Racing by Infraction
- Sport Rock Workout by Infraction
- Sport Trap Rock by Infraction
- Upbeat Rock Energetic by Infraction

---

## 6. INTERFACE E MENUS

### 6.1 Sistema de Menus
- **Menu Principal**: Jogar, Selecionar Carros, Selecionar Mapas, Opções, Sair
- **Seleção de Carros**: Escolha de veículos para P1 e P2
- **Seleção de Mapas**: Escolha de pista
- **Opções**: Configurações de áudio, vídeo e controles

### 6.2 HUD do Jogo
- **Posições**: Ranking dos carros em tempo real
- **Tempo**: Cronômetro da corrida
- **Velocidade**: Velocidade atual do carro
- **Drift Score**: Pontuação de derrapagem (modo drift ativo)
- **FPS**: Quadros por segundo (opcional)
- **Debug IA**: Informações da inteligência artificial (opcional)

### 6.3 Sistema de Câmera
- **Seguimento Suave**: Câmera segue o carro principal
- **Zoom Configurável**: Ajuste de distância de visualização
- **Transições**: Movimento suave entre posições

---

## 7. SISTEMA DE CONFIGURAÇÕES

### 7.1 Configurações de Áudio
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
  }
}
```

### 7.2 Configurações de Vídeo
```json
{
  "video": {
    "resolucao": [1280, 720],
    "fullscreen": false,
    "tela_cheia_sem_bordas": false,
    "vsync": true,
    "fps_max": 60,
    "qualidade_alta": true
  }
}
```

### 7.3 Configurações de Controles
```json
{
  "controles": {
    "sensibilidade_volante": 1.0,
    "inverter_volante": false,
    "auto_centro": true
  }
}
```

### 7.4 Configurações de Jogo
```json
{
  "jogo": {
    "dificuldade_ia": 1.0,
    "modo_drift": true,
    "mostrar_fps": false,
    "mostrar_debug": false
  }
}
```

---

## 8. ARQUITETURA TÉCNICA

### 8.1 Estrutura Modular
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

### 8.2 Fluxo de Execução
1. **Inicialização**: Carregamento de configurações e assets
2. **Menu Principal**: Seleção de opções e configurações
3. **Seleção de Carros/Mapas**: Escolha de veículos e pistas
4. **Loop de Jogo**: Física, IA, renderização e input
5. **Finalização**: Salvamento de dados e retorno ao menu

### 8.3 Tecnologias Utilizadas
- **Python 3.10+**: Linguagem de programação principal
- **Pygame**: Biblioteca para renderização e input
- **JSON**: Formato para configurações e dados
- **Algoritmo Pure Pursuit**: Navegação da IA

---

## 9. SISTEMA DE CARROS

### 9.1 Carros Disponíveis
O jogo inclui 12 carros diferentes, cada um com:
- **Sprite Único**: Imagem personalizada para cada veículo
- **Sprite de Seleção**: Imagem para interface de seleção
- **Configuração Padrão**: Posição e parâmetros iniciais

### 9.2 Adicionando Novos Carros
1. **Adicionar Sprite**: Colocar imagem em `assets/images/cars/`
2. **Adicionar Sprite de Seleção**: Colocar imagem em `assets/images/car_selection/`
3. **Configurar**: Adicionar entrada em `CARROS_DISPONIVEIS`

---

## 10. SISTEMA DE EFEITOS VISUAIS

### 10.1 Partículas
- **Fumaça de Drift**: Efeito visual durante derrapagem
- **Efeitos de Turbo**: Partículas durante uso do turbo
- **Sistema de Emissão**: Controle de taxa e direção das partículas

### 10.2 Efeitos de Debug
- **Visualização da IA**: Mostra pontos alvo e trajetórias
- **Debug de Rota**: Exibe waypoints e checkpoints
- **Informações de Performance**: FPS e estatísticas

---

## 11. SISTEMA DE CORRIDA

### 11.1 Gerenciador de Corrida
- **Contagem Regressiva**: Semaforo antes do início
- **Cronômetro**: Tempo total da corrida
- **Posicionamento**: Ranking em tempo real
- **Finalização**: Detecção de chegada e pódio

### 11.2 Sistema de Drift (Opcional)
- **Pontuação**: Baseada em velocidade e ângulo
- **Combo**: Multiplicadores por sequência de drifts
- **Decay**: Redução automática de pontos ao longo do tempo
- **Efeitos Visuais**: Fumaça e partículas durante drift

---

## 12. REQUISITOS DO SISTEMA

### 12.1 Requisitos Mínimos
- **Sistema Operacional**: Windows 10
- **Processador**: Intel Core i3 ou equivalente
- **Memória RAM**: 4 GB
- **Espaço em Disco**: 500 MB
- **Python**: 3.10 ou superior
- **Pygame**: Última versão estável

### 12.2 Requisitos Recomendados
- **Sistema Operacional**: Windows 11
- **Processador**: Intel Core i5 ou superior
- **Memória RAM**: 8 GB
- **Espaço em Disco**: 1 GB
- **Resolução**: 1920x1080 ou superior

---

## 13. CONTROLES DE DEBUG

### 13.1 Teclas de Debug
- **F1**: Ativar/desativar debug da IA
- **F2**: Ativar/desativar debug da rota
- **F3**: Gravar waypoints
- **F4**: Salvar waypoints gravados
- **F5**: Salvar checkpoints
- **F6**: Carregar checkpoints
- **F7**: Ativar/desativar modo edição de checkpoints
- **F8**: Limpar todos os checkpoints
- **F9**: Trocar para próximo mapa
- **F11**: Mostrar FPS
- **C**: Limpar waypoints gravados

---

## 14. ROADMAP E FUTURAS IMPLEMENTAÇÕES

### 14.1 Funcionalidades Planejadas
- **Sistema de Multiplayer Online**: Corridas em rede
- **Editor de Mapas**: Criação visual de pistas
- **Sistema de Achievements**: Conquistas e troféus
- **Modo Time Trial**: Corrida contra o tempo
- **Sistema de Replay**: Gravação e reprodução de corridas
- **Mais Carros**: Expansão da frota de veículos
- **Novos Mapas**: Adição de pistas temáticas

### 14.2 Melhorias Técnicas
- **Otimização de Performance**: Melhor uso de recursos
- **Sistema de Mods**: Suporte a modificações da comunidade
- **Interface Melhorada**: Design mais moderno e intuitivo
- **Sistema de Save**: Salvamento de progresso e configurações

---

## 15. CONCLUSÃO

Turbo Racer representa um projeto ambicioso de jogo de corrida 2D que combina elementos clássicos do gênero com mecânicas modernas e inovadoras. O sistema de física realista, IA inteligente e editor visual de checkpoints proporcionam uma experiência única e personalizável.

A arquitetura modular e escalável permite fácil expansão e manutenção, enquanto a documentação técnica detalhada facilita o desenvolvimento futuro e contribuições da comunidade.

O jogo está posicionado para oferecer uma experiência de corrida divertida e acessível, adequada tanto para jogadores casuais quanto para entusiastas do gênero, com potencial significativo para crescimento e evolução através de atualizações e conteúdo adicional.

---

**Documento elaborado por:** JeanM  
**Data de criação:** Setembro 2025  
**Versão do documento:** 2.0  
**Status:** Finalizado
