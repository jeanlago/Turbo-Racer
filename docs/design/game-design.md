# 🎮 Game Design Document - Turbo Racer

**Versão:** 2.0  
**Data:** Dezembro 2024  
**Desenvolvedor:** Jean Marins e Jayson Sales  
**Gênero:** Corrida Arcade 2D Top-Down  
**Plataforma:** PC (Windows)  
**Motor:** Python + Pygame  

---

## 1. Visão Geral do Jogo

### 1.1 Conceito Principal
Turbo Racer é um jogo de corrida arcade 2D desenvolvido em Python com Pygame, focado em proporcionar uma experiência de corrida divertida e acessível com física realista, sistema de derrapagem (drift) e inteligência artificial avançada. O jogo combina elementos clássicos de corrida com mecânicas modernas de gameplay.

### 1.2 Proposta de Valor
- **Física Realista** - Sistema de física avançado com diferentes tipos de tração
- **Múltiplos Modos** - 1 jogador, 2 jogadores e modo drift
- **IA Inteligente** - Algoritmo Pure Pursuit para navegação
- **Sistema de Drift** - Derrapagem realista com pontuação
- **Interface Moderna** - HUD limpo e intuitivo
- **Modularidade** - Fácil adição de mapas e carros

### 1.3 Público-Alvo
- **Idade:** 12+ anos
- **Interesse:** Jogos de corrida, arcade, indie
- **Plataforma:** PC (Windows)
- **Experiência:** Iniciante a avançado

---

## 2. Mecânicas de Jogo

### 2.1 Controles Básicos
- **WASD** - Movimento (Jogador 1)
- **Setas** - Movimento (Jogador 2)
- **Shift** - Turbo (Jogador 1)
- **Ctrl** - Turbo (Jogador 2)
- **ESC** - Pausar/Menu
- **H** - Alternar HUD

### 2.2 Sistema de Física
- **Tipos de Tração:**
  - **RWD** - Tração traseira (pode fazer drift)
  - **FWD** - Tração frontal (estável, sem drift)
  - **AWD** - Tração integral (drift limitado)
- **Velocidade:** 0-200 km/h
- **Derrapagem:** Baseada em velocidade e ângulo
- **Colisões:** Realistas com rebote

### 2.3 Sistema de Drift
- **Ativação:** Espaço (P1) ou Shift (P2)
- **Pontuação:** Baseada em velocidade e ângulo
- **Combo:** Multiplicador por derrapagens consecutivas
- **Tempo:** 2 minutos para acumular pontos

### 2.4 Sistema de Turbo
- **Ativação:** Shift (P1) ou Ctrl (P2)
- **Duração:** 0.9 segundos
- **Cooldown:** 2.5 segundos
- **Efeito:** 1.25x velocidade

---

## 3. Modos de Jogo

### 3.1 Modo 1 Jogador
- **Objetivo:** Completar checkpoints contra IA
- **Câmera:** Dinâmica (zoom baseado na velocidade)
- **IA:** Algoritmo Pure Pursuit
- **Checkpoints:** 11 por volta

### 3.2 Modo 2 Jogadores
- **Objetivo:** Primeiro a completar todos os checkpoints
- **Tela:** Split-screen vertical
- **Câmeras:** Independentes para cada jogador
- **Checkpoints:** Separados para cada jogador
- **Vitória:** Parada automática quando alguém vence

### 3.3 Modo Drift
- **Objetivo:** Acumular pontos em 2 minutos
- **Câmera:** Dinâmica
- **Pontuação:** Baseada em velocidade e ângulo
- **Combo:** Multiplicador por derrapagens consecutivas
- **Fim:** Tempo esgotado ou ESC

---

## 4. Interface e HUD

### 4.1 HUD Principal
- **Velocímetro** - Velocidade atual com ponteiro
- **Nitro** - Carga de turbo com efeito visual
- **Pause** - Indicador de jogo pausado

### 4.2 HUD Drift
- **Tempo** - Cronômetro de 2 minutos
- **Pontuação** - Pontos acumulados
- **Combo** - Multiplicador atual

### 4.3 HUD 2 Jogadores
- **Split-screen** - HUD adaptado para cada metade
- **Checkpoints** - Separados por jogador
- **Cores** - Azul (P1), Amarelo (P2)

---

## 5. Sistema de Menus

### 5.1 Menu Principal
- **JOGAR** - Seleção de modo
- **SELECIONAR CARROS** - Escolha de veículos
- **SELECIONAR MAPAS** - Escolha de pistas
- **OPÇÕES** - Configurações
- **SAIR** - Encerrar jogo

### 5.2 Seleção de Modo
- **1 JOGADOR** / **2 JOGADORES**
- **CORRIDA** / **DRIFT**
- **INICIAR JOGO** - Confirmar
- **VOLTAR** - Menu principal

### 5.3 Opções
- **ÁUDIO** - Volume e música
- **VÍDEO** - Resolução e qualidade
- **CONTROLES** - Teclas e sensibilidade
- **IDIOMA** - Português, Inglês, etc.

---

## 6. Sistema de Carros

### 6.1 Carros Disponíveis
- **Nissan 350Z** - RWD, drift
- **Honda Civic** - FWD, estável
- **Subaru Impreza** - AWD, equilibrado
- **Toyota Supra** - RWD, velocidade
- **Mazda RX-7** - RWD, drift técnico

### 6.2 Características
- **Nome** - Identificação
- **Tipo de Tração** - RWD/FWD/AWD
- **Sprite** - Visual no jogo
- **Sprite Seleção** - Visual na oficina
- **Tamanho** - Dimensões na oficina
- **Posição** - Localização na oficina

---

## 7. Sistema de Mapas

### 7.1 Mapas Disponíveis
- **Map_1** - Pista principal
- **Map_2** - Pista técnica
- **Map_3** - Pista de velocidade

### 7.2 Elementos dos Mapas
- **Pista** - Laranja (transitável)
- **Limites** - Verde (não transitável)
- **Checkpoints** - Magenta (área transitável)
- **Guias** - Amarelo (linha de largada)

---

## 8. Sistema de Áudio

### 8.1 Música
- **Menu** - Tema principal
- **Jogo** - Música de corrida
- **Drift** - Música de derrapagem
- **Vitória** - Tema de vitória

### 8.2 Efeitos Sonoros
- **Motor** - Som do motor
- **Turbo** - Som do turbo
- **Drift** - Som da derrapagem
- **Checkpoint** - Som de checkpoint
- **Colisão** - Som de colisão

---

## 9. Sistema de IA

### 9.1 Algoritmo Pure Pursuit
- **Navegação** - Segue checkpoints
- **Lookahead** - Distância baseada na velocidade
- **Steering** - Ângulo de direção calculado
- **Recuperação** - Detecta situações problemáticas

### 9.2 Parâmetros Configuráveis
- **Wheelbase** - Distância entre eixos
- **Lookahead** - Distância de antecipação
- **Velocidade** - Mínima e máxima
- **Ganho** - Sensibilidade de direção

---

## 10. Sistema de Vitória

### 10.1 Modo Corrida
- **Objetivo** - Completar todos os checkpoints
- **Detecção** - Automática quando checkpoint_atual >= len(checkpoints)
- **Parada** - Carros param imediatamente
- **Tela** - Overlay com vencedor

### 10.2 Modo Drift
- **Objetivo** - Acumular pontos em 2 minutos
- **Fim** - Tempo esgotado
- **Tela** - Pontuação final

---

## 11. Sistema de Configuração

### 11.1 Arquivo config.json
- **Áudio** - Volume e música
- **Vídeo** - Resolução e qualidade
- **Controles** - Teclas e sensibilidade
- **Jogo** - Dificuldade e opções

### 11.2 Carregamento Dinâmico
- **Inicialização** - Carrega configurações padrão
- **Sobrescrita** - Aplica configurações do JSON
- **Persistência** - Salva alterações automaticamente

---

## 12. Sistema de Desenvolvimento

### 12.1 Estrutura Modular
- **main.py** - Loop principal
- **core/** - Módulos principais
- **assets/** - Recursos do jogo
- **docs/** - Documentação

### 12.2 Padrões de Código
- **Python 3.10+** com type hints
- **Pygame** para renderização
- **Modular** e bem documentado
- **Configurável** via JSON

---

## 13. Roadmap Futuro

### 13.1 Versão 2.1
- **Novos Mapas** - Pistas adicionais
- **Novos Carros** - Veículos extras
- **Efeitos Visuais** - Partículas melhoradas
- **Sons** - Efeitos sonoros adicionais

### 13.2 Versão 3.0
- **Modo Online** - Multiplayer online
- **Editor de Mapas** - Criação de pistas
- **Sistema de Ranking** - Competições
- **Mods** - Suporte a modificações

---

**Documento atualizado em:** Dezembro 2024  
**Versão:** 2.0  
**Próximo:** [API Reference](../API.md)
