# 🏎️ Turbo Racer

Um mini-jogo de corrida top-down desenvolvido em **Python** com **Pygame**.
O objetivo é controlar carros em uma pista baseada em imagem, com física simples de aceleração, frenagem, derrapagem e colisões.

---

## 📂 Estrutura do Projeto

Turbo-Racer/
├─ assets/ # Recursos do jogo (sprites e mapas)
│ └─ images/
│ ├─ car_sprites/ # Sprites dos carros (red.png, blue.png, etc.)
│ └─ maps/ # Mapas da pista (Map_1.png, etc.)
│
├─ core/
│ ├─ carro.py # Classe Carro (física, direção, colisões)
│ └─ pista.py # Funções de pista (carregar e validar pixels)
│
├─ utils/
│ └─ cores.py # Funções auxiliares para manipulação de cores (RGB/HSV)
│
├─ config.py # Constantes globais (tela, FPS, caminhos, paleta da pista)
├─ main.py # Ponto de entrada (inicializa e roda o loop principal)
└─ README.md # Este arquivo

---

## 🎮 Controles

- **Carro Vermelho (Player 1)**
  - Acelerar: **W**
  - Frear / Ré: **S**
  - Virar Direita: **D**
  - Virar Esquerda: **A**

- **Carro Azul (Player 2)**
  - Acelerar: **Seta ↑**
  - Frear / Ré: **Seta ↓**
  - Virar Direita: **Seta →**
  - Virar Esquerda: **Seta ←**

---

## ⚙️ Requisitos

- Python **3.10+**
- Biblioteca [Pygame](https://www.pygame.org/)

Instalação do Pygame:

```bash
pip3 install pygame
