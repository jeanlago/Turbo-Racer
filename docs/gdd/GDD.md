# Turbo Racer — Game Design Document (GDD)

Versão: 0.1  |  Data: 2025-09-26

## Visão Geral
- Título: Turbo Racer
- Gênero: Corrida arcade com drift scoring e nitro
- Plataforma-alvo: Desktop (Python)
- Público: Jogadores casuais e entusiastas de arcade racing
- Pitch: Corridas top-down rápidas com física de derrapagem estilizada, nitro e pistas modulares. Pontuação por drift, checkpoints e contra-relógio.

## Objetivos do Jogo
- Completar voltas passando por checkpoints dentro do tempo.
- Maximizar pontuação de drift conforme o ângulo e duração.
- Gerenciar nitro estrategicamente para ganhar velocidade em retas.

## Mecânicas Principais
- Condução e Física: modelo de física customizado do carro, aceleração, frenagem, derrapagem, atrito e marcas de pneu.
  - Implementação principal: `src/core/carro_fisica.py`, `src/core/carro.py`
  - Referência técnica: `docs/tech/FISICA_CARROS.md`
- Drift Scoring: pontuação por derrapagem contínua com multiplicadores.
  - Implementação: `src/core/drift_scoring.py`
- Nitro: consumo/recarregamento e efeito visual.
  - Ícones/UI: `assets/images/icons/nitro.png`, `assets/images/icons/nitro_vazio.png`
  - Efeitos: `assets/images/effects/nitro/`
- Checkpoints e Voltas: validação de sequência e conclusão de volta.
  - Implementação: `src/core/checkpoint_manager.py`
  - Dados de guias/checkpoints: `assets/images/maps/guides/*.json`
- HUD: velocímetro, nitro, ponteiro e UI de corrida.
  - Implementação: `src/core/hud.py`
  - Assets: `assets/images/icons/velocimetro.png`, `assets/images/icons/ponteiro.png`
- Skidmarks e Partículas: efeitos visuais de derrapagem e fumaça.
  - Implementação: `src/core/skidmarks.py`, `src/core/particulas.py`
- Câmera: follow com suavização.
  - Implementação: `src/core/camera.py`

## Modos de Jogo
- Corrida Padrão: completar N voltas passando por todos os checkpoints na ordem.
- Contra-relógio: alcançar o melhor tempo; possibilidade de ghost (futuro).
- Desafio de Drift: focado em pontuação de derrapagem (base técnica já em `drift_scoring`).
- Orquestração: `src/core/corrida.py`, `src/core/game_modes.py`, `src/main.py`

## Conteúdo
- Carros: sprites em `assets/images/cars/` e para seleção em `assets/images/car_selection/`.
- Pistas: tiles em `assets/images/pistas/` e mapas prontos em `assets/images/maps/Mapa_*.png`.
- Guias/Checkpoints: `assets/images/maps/guides/` (png de guia e json de checkpoints).
- UI: `assets/images/ui/`.
- Personagens: em `assets/images/characters/` (potencial para modos futuros).
- Fontes: `assets/fonts/PixeloidSans.ttf`.
- Áudio: músicas em `assets/sounds/music/`.

## Progressão e Regras
- Voltas: número configurável por pista (ver `data/config.json`).
- Checkpoints: sequência obrigatória conforme JSON de cada pista.
- Drift: pontuação contínua com perda ao colisão/parada.
- Nitro: barra recarregável; esvazia ao uso; efeito visual em exaustor.

## Interface e HUD
- Velocímetro com ponteiro (rotação baseada na velocidade).
- Barra de nitro com estados cheio/vazio.
- Popup de música e controle de trilha: `src/core/popup_musica.py`, `src/core/musica.py`.
- Menu e Oficina (seleção de carro): `src/core/menu.py`, `assets/images/ui/oficina.png`.

## Arte e Direção Visual
- Estilo pixel art retro.
- Paleta coerente entre carros, pistas e UI.
- Efeitos de derrapagem e fumaça: `assets/images/effects/smoke/`.

## Áudio e Trilha
- Faixas licenciadas armazenadas em `assets/sounds/music/`.
- Sistema de música com troca e popup: `src/core/musica.py`, `src/core/popup_musica.py`.

## Dados e Configurações
- Configurações gerais: `data/config.json`
- Ponteiro/velocímetro: `data/ponteiro_config.json`
- Mapas personalizados: `data/mapas_personalizados.json`, `data/mapa_personalizado.json`
- Backups de checkpoints: `data/checkpoints_backup.json`

## Ferramentas e Pipeline
- Editor de Checkpoints: `tools/checkpoint_editor.py` (ver `tools/README.md`).
- Guia para adicionar mapas: `docs/guides/adding-maps.md`.
- API interna/estrutura: `docs/API.md`.
- Changelog: `docs/CHANGELOG.md`.

## GameObjects
- Especificações detalhadas das entidades do jogo (Carro, Pista/Segmentos, Checkpoint, Partícula, Skidmark, HUD, Câmera, Música) estão em `docs/gdd/GameObjects.md`.

## Estrutura de Código (alto nível)
- Entrada e loop principal: `src/main.py`
- Núcleo do jogo: `src/core/*`
- Configuração: `src/config.py`

## Requisitos Técnicos
- Python 3.x
- Bibliotecas listadas no projeto (ver `README.md`).
- Sistema de arquivos conforme árvore do repositório.

## Tarefas Futuras (Backlog)
- Ghost no contra-relógio
- IA de oponentes mais avançada (`src/core/ia.py`)
- Sistema de campeonatos e desbloqueáveis
- Salvamento de replays e leaderboards

## Referências Rápidas
- Design: `docs/design/game-design.md`
- Tech: `docs/tech/FISICA_CARROS.md`
- README: `README.md`

---
Este GDD reflete o estado atual do repositório e deve ser atualizado conforme o desenvolvimento evoluir.
