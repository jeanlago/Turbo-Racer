# GameObjects — Turbo Racer

Este documento descreve as principais entidades do jogo, seus atributos, comportamentos, dependências de assets e integração no código.

## Sumário
- Carro
- Pista e Segmentos
- Checkpoint
- HUD
- Câmera
- Partícula (efeitos)
- Skidmark (marcas de pneu)
- Música/Trilha

---

## Carro
- Código: `src/core/carro.py`, `src/core/carro_fisica.py`
- Sprites: `assets/images/cars/`, seleção: `assets/images/car_selection/`
- Atributos chave:
  - massa, tração, aceleração, frenagem, arrasto, grip, torque de direção
  - estado: velocidade, direção, ângulo de drift, nitro_atual, dano (se aplicável)
- Comportamentos:
  - entrada do jogador/IA (acelerar, frear, virar)
  - atualização de física por tick
  - uso de nitro (consumo, cooldown)
  - emissão de partículas (fumaça) e skidmarks ao derrapar
- UI relacionada: velocímetro, nitro (em `src/core/hud.py`)

## Pista e Segmentos
- Código: `src/core/pista.py`
- Tiles: `assets/images/pistas/`
- Mapas: `assets/images/maps/Mapa_*.png`
- Funções:
  - Carregamento de layout, grip por tile, limites de colisão (se houver)
  - Dados auxiliares: guias/checkpoints (`assets/images/maps/guides/*.json`)

## Checkpoint
- Código: `src/core/checkpoint_manager.py`
- Dados: `assets/images/maps/guides/*_checkpoints.json`
- Atributos:
  - ordem, posição, raio/tolerância, id da volta
- Comportamento:
  - valida sequência, registra passagem, sinaliza fim de volta

## HUD
- Código: `src/core/hud.py`
- Assets: `assets/images/icons/velocimetro.png`, `assets/images/icons/ponteiro.png`, `assets/images/icons/nitro.png`, `assets/images/icons/nitro_vazio.png`
- Elementos:
  - velocímetro (ponteiro com rotação baseada na velocidade)
  - barra de nitro (cheio/vazio)
  - pontuação de drift (integra `src/core/drift_scoring.py`)

## Câmera
- Código: `src/core/camera.py`
- Comportamento:
  - segue o carro-alvo com suavização e ajuste de zoom dependente da velocidade

## Partícula (Efeitos)
- Código: `src/core/particulas.py`
- Assets: `assets/images/effects/smoke/`, `assets/images/effects/nitro/`
- Uso:
  - fumaça ao derrapar, jato de nitro ao ativar

## Skidmark (Marcas de Pneu)
- Código: `src/core/skidmarks.py`
- Comportamento:
  - renderiza trilhas de derrapagem baseadas no ângulo e intensidade

## Música/Trilha
- Código: `src/core/musica.py`, `src/core/popup_musica.py`
- Assets: `assets/sounds/music/*.mp3`
- Comportamento:
  - tocar/pausar/trocar faixas, popup informativo durante a corrida

---

## Integração e Fluxo
- Loop principal: `src/main.py`
- Organização de modos: `src/core/game_modes.py`, `src/core/corrida.py`
- IA (oponentes): `src/core/ia.py` (escopo futuro/expansível)

## Notas de Implementação
- Parametrizações adicionais podem residir em `data/config.json` e arquivos específicos em `data/*`.
- Para adicionar novos objetos, manter consistência de diretórios de assets e registrar no GDD.
