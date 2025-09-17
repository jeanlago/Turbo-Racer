# 🏎️ Turbo Racer

Um jogo de corrida top-down desenvolvido em **Python** com **Pygame**, com sistema completo de física, IA, múltiplos mapas e editor de checkpoints visual.

---

## Funcionalidades Principais

-  **Sistema de Corrida Completo** - Física realista, derrapagem, turbo e colisões
-  **IA Inteligente** - Carros controlados por IA que seguem checkpoints
-  **Múltiplos Mapas** - Sistema escalável para adicionar quantos mapas quiser
-  **Editor Visual de Checkpoints** - Crie e edite checkpoints arrastando e soltando
-  **Sistema de Música** - Múltiplas faixas com controles de volume
-  **Modo Drift** - Sistema de pontuação por derrapagem
-  **Configurações Avançadas** - Resolução, fullscreen, controles personalizáveis

---

## 📂 Estrutura do Projeto

```text
Turbo-Racer-1/
├─ assets/
│  ├─ images/
│  │  ├─ cars/                    # Sprites dos carros
│  │  ├─ car_selection/           # Sprites para seleção de carros
│  │  ├─ maps/                    # Mapas do jogo
│  │  │  ├─ Map_1.png
│  │  │  └─ guides/               # Guias e checkpoints
│  │  │     ├─ Map_1_guides.png
│  │  │     └─ Map_1_checkpoints.json
│  │  ├─ effects/                 # Efeitos visuais
│  │  └─ ui/                      # Interface do usuário
│  └─ sounds/
│     └─ music/                   # Músicas do jogo
├─ src/
│  ├─ main.py                     # Ponto de entrada principal
│  ├─ config.py                   # Configurações e constantes
│  └─ core/
│     ├─ carro.py                 # Física e controle dos carros
│     ├─ pista.py                 # Carregamento e detecção de pista
│     ├─ camera.py                # Sistema de câmera
│     ├─ corrida.py               # Gerenciador de corrida
│     ├─ ia_simples.py            # Inteligência artificial
│     ├─ checkpoint_manager.py    # Editor de checkpoints
│     ├─ menu.py                  # Sistema de menus
│     ├─ musica.py                # Gerenciador de música
│     ├─ particulas.py            # Efeitos de partículas
│     └─ popup_musica.py          # Interface de música
├─ checkpoints.json               # Checkpoints salvos
├─ config.json                    # Configurações do usuário
└─ README.md
```

---

## 🎮 Controles

### **Carro 1 (Player 1)**
- **Acelerar:** W
- **Frear/Ré:** S
- **Virar Direita:** D
- **Virar Esquerda:** A
- **Turbo:** Shift Esquerdo
- **Drift:** Espaço

### **Carro 2 (Player 2)**
- **Acelerar:** Seta ↑
- **Frear/Ré:** Seta ↓
- **Virar Direita:** Seta →
- **Virar Esquerda:** Seta ←
- **Turbo:** Ctrl Direito
- **Drift:** Shift

### **Controles Gerais**
- **M:** Alternar música
- **N:** Próxima música
- **F11:** Alternar modo de tela
- **ESC:** Voltar ao menu

### **Editor de Checkpoints (F7)**
- **F5:** Salvar checkpoints
- **F6:** Carregar checkpoints
- **F7:** Ativar/desativar modo edição
- **F8:** Limpar todos os checkpoints
- **F9:** Trocar para próximo mapa
- **Clique e Arrastar:** Mover checkpoints
- **Clique em área vazia:** Adicionar checkpoint
- **DEL:** Remover checkpoint selecionado

---

## ✏️ Como Executar

### **Requisitos**
- Python **3.10+**
- Biblioteca [Pygame](https://www.pygame.org/)

### **Instalação**
```bash
# Instalar Pygame
pip install pygame

# Executar o jogo
python src/main.py
```

---

## 🗺️ Sistema de Mapas

### **Adicionar Novo Mapa**

1. **Coloque os arquivos** na estrutura:
   ```
   assets/images/maps/
   ├── SeuMapa.png
   └── guides/
       ├── SeuMapa_guides.png
       └── SeuMapa_checkpoints.json (criado automaticamente)
   ```

2. **Adicione no config.py**:
   ```python
   "SeuMapa": {
       "nome": "Nome do Mapa",
       "arquivo_mapa": os.path.join(DIR_MAPS, "SeuMapa.png"),
       "arquivo_guias": os.path.join(DIR_MAPS_GUIDES, "SeuMapa_guides.png"),
       "arquivo_checkpoints": os.path.join(DIR_MAPS_GUIDES, "SeuMapa_checkpoints.json"),
       "waypoints_fallback": [(x1, y1), (x2, y2), ...]
   }
   ```

3. **Crie os checkpoints** usando o editor visual (F7)

### **Editor de Checkpoints**
- **Ative o modo edição** (F7)
- **Clique e arraste** para mover checkpoints
- **Clique em área vazia** para adicionar novos
- **Salve** com F5

---

## ⚙️ Configurações

### **Arquivo config.json**
```json
{
  "audio": {
    "volume_master": 1.0,
    "volume_musica": 0.8,
    "musica_habilitada": true,
    "musica_aleatoria": false
  },
  "video": {
    "resolucao": [1280, 720],
    "fullscreen": false,
    "fps_max": 60
  },
  "jogo": {
    "modo_drift": true,
    "mostrar_fps": true,
    "mostrar_debug": false
  }
}
```

---

## 🎯 Funcionalidades Avançadas

### **Sistema de IA**
- Carros controlados por IA seguem checkpoints automaticamente
- Algoritmo Pure Pursuit para navegação suave
- Detecção de colisões e recuperação automática

### **Física Realista**
- Aceleração e frenagem progressivas
- Sistema de derrapagem com pontuação
- Colisões com rebote e perda de velocidade
- Turbo com cooldown

### **Sistema de Música**
- Múltiplas faixas de música
- Controles de volume independentes
- Modo aleatório
- Interface visual de música

### **Modo Drift**
- Pontuação baseada em velocidade e ângulo
- Efeitos visuais de fumaça
- Sistema de combo
- Decay automático de pontos

---

## 🛠️ Desenvolvimento

### **Estrutura do Código**
- **Modular:** Cada funcionalidade em seu próprio módulo
- **Escalável:** Fácil adicionar novos mapas e carros
- **Configurável:** Todas as configurações em arquivos JSON
- **Português:** Código e variáveis em português

### **Adicionando Novos Carros**
1. Adicione o sprite em `assets/images/cars/`
2. Configure em `CARROS_DISPONIVEIS` no `main.py`
3. Adicione sprite de seleção em `assets/images/car_selection/`

### **Personalizando Física**
- Ajuste constantes em `config.py`
- Modifique `core/carro.py` para física personalizada
- Configure parâmetros de IA em `core/ia_simples.py`

---

## 📝 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.

---