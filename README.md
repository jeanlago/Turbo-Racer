# 🏎️ Turbo Racer

Um mini-jogo de corrida top-down desenvolvido em **Python** com **Pygame**.
O objetivo é controlar carros em uma pista baseada em imagem, com física simples de aceleração, frenagem, derrapagem e colisões.

---

## 📂 Estrutura do Projeto
```text
Turbo-Racer/
├─ assets/
│  └─ images/
│     ├─ car_sprites/
│     │  ├─ blue.png
│     │  └─ red.png
│     └─ maps/
│        └─ Map_1.png
├─ src/
│  ├─ main.py              # ponto de entrada do jogo
│  ├─ config.py            # constantes (tela, FPS, caminhos, paleta/HSV)
│  ├─ core/
│  │  ├─ carro.py          # classe Carro (física, direção, colisões)
│  │  └─ pista.py          # carregar pista e checar se o pixel é dirigível
│  └─ utils/
│     └─ cores.py          # utilitários de cor (RGB/HSV)
│
└─ README.md
```
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
