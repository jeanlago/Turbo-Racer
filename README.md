# 🏎️ Turbo Racer

Um jogo de corrida top-down desenvolvido em **Python** com **Pygame**, com sistema completo de física, IA, múltiplos mapas e editor de checkpoints visual.

---

## Funcionalidades Principais

-  **Sistema de Corrida Completo** - Física realista com tipos de tração, derrapagem, turbo e colisões
-  **IA Inteligente** - Carros controlados por IA melhorada que seguem checkpoints
-  **Múltiplos Mapas** - Sistema escalável para adicionar quantos mapas quiser
-  **Editor Visual de Checkpoints** - Crie e edite checkpoints arrastando e soltando
-  **Sistema de Música** - Múltiplas faixas com controles de volume
-  **Modo Drift** - Sistema de pontuação por derrapagem
-  **HUD Personalizado** - Interface moderna com minimapa e informações detalhadas
-  **Configurações Avançadas** - Resolução, fullscreen, controles personalizáveis

---

## 📚 Documentação

### **Game Design Document (GDD)**
- **[GDD_Turbo_Racer.md](docs/gdd/GDD_Turbo_Racer.md)** - Documento completo de design do jogo
  - Visão geral e conceito principal
  - Mecânicas de jogo detalhadas
  - Sistema de IA e física
  - Arquitetura técnica
  - Roadmap e futuras implementações

### **Documentação Técnica**
- **[DOCUMENTACAO.md](docs/tech/DOCUMENTACAO.md)** - Documentação técnica completa
  - Arquitetura do sistema
  - Módulos principais
  - API Reference
  - Exemplos de uso
  - Troubleshooting

- **[GAME_OBJECTS_Turbo_Racer.md](docs/tech/GAME_OBJECTS_Turbo_Racer.md)** - Lista detalhada de objetos do jogo
  - Objetos principais e sistemas
  - Propriedades e métodos
  - HierarquIA de objetos
  - Relacionamentos entre sistemas

### **GuIAs de Desenvolvimento**
- **[COMO_ADICIONAR_MAPAS.md](docs/guides/COMO_ADICIONAR_MAPAS.md)** - GuIA para adicionar novos mapas

### **Ferramentas de Debug**
- **[tools/README.md](tools/README.md)** - Ferramentas de desenvolvimento e debug
  - `test_debug.py` - Teste básico de funcionalidades
  - `debug_IA_travada.py` - Debug visual de checkpoints e IA
  - `test_audio.py` - Teste do sistema de áudio

### **Dados e Configurações**
- **[data/README.md](data/README.md)** - Dados do usuário e configurações
  - `config.json` - Configurações do usuário (áudio, vídeo, controles)
  - `checkpoints_backup.json` - Backup de checkpoints legado

---

## 📂 Estrutura do Projeto

```text
Turbo-Racer/
├─ assets/
│  ├─ images/
│  │  ├─ cars/                    # Sprites dos carros
│  │  ├─ car_selection/           # Sprites para seleção de carros
│  │  ├─ maps/                    # Mapas do jogo
│  │  │  ├─ Map_1.png
│  │  │  └─ guides/               # GuIAs e checkpoints
│  │  │     ├─ Map_1_guides.png
│  │  │     └─ Map_1_checkpoints.json
│  │  ├─ effects/                 # Efeitos visuais
│  │  ├─ icons/                   # Ícones da interface
│  │  └─ ui/                      # Interface do usuário
│  └─ sounds/
│     └─ music/                   # Músicas do jogo
├─ docs/                          # Documentação do projeto
│  ├─ gdd/                        # Game Design Documents
│  │  └─ GDD_Turbo_Racer.md       # Documento de design do jogo
│  ├─ tech/                       # Documentação técnica
│  │  ├─ DOCUMENTACAO.md          # Documentação técnica completa
│  │  └─ GAME_OBJECTS_Turbo_Racer.md # Lista de objetos do jogo
│  └─ guides/                     # GuIAs de desenvolvimento
│     └─ COMO_ADICIONAR_MAPAS.md  # GuIA para adicionar mapas
├─ tools/                         # Ferramentas de debug e teste
│  ├─ test_debug.py               # Teste básico de funcionalidades
│  ├─ debug_IA_travada.py         # Debug visual de checkpoints
│  ├─ test_audio.py               # Teste do sistema de áudio
│  └─ README.md                   # Documentação das ferramentas
├─ data/                          # Dados e configurações do usuário
│  ├─ config.json                 # Configurações do usuário
│  ├─ checkpoints_backup.json     # Backup de checkpoints legado
│  └─ README.md                   # Documentação dos dados
├─ src/
│  ├─ main.py                     # Ponto de entrada principal
│  ├─ config.py                   # Configurações e constantes
│  └─ core/
│     ├─ carro.py                 # Física e controle dos carros
│     ├─ pista.py                 # Carregamento e detecção de pista
│     ├─ camera.py                # Sistema de câmera
│     ├─ corrida.py               # GerencIAdor de corrida
│     ├─ IA_v2.py       # InteligêncIA artificIAl melhorada
│     ├─ checkpoint_manager.py    # Editor de checkpoints
│     ├─ menu.py                  # Sistema de menus
│     ├─ musica.py                # GerencIAdor de música
│     ├─ particulas.py            # Efeitos de partículas
│     └─ popup_musica.py          # Interface de música
├─ checkpoints.json               # Checkpoints salvos
├─ config.json                    # Configurações do usuário
├─ COMO_ADICIONAR_MAPAS.md        # GuIA para adicionar mapas
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
- **M:** Próxima música
- **N:** Música anterior
- **H:** Alternar HUD completo
- **F1:** Ativar/desativar debug da IA
- **ESC:** Pausar/despausar ou voltar ao menu

### **Editor de Checkpoints**
- **F7:** Ativar/desativar modo edição
- **F5:** Salvar checkpoints
- **F6:** Carregar checkpoints
- **F8:** Limpar todos os checkpoints
- **F10:** Mostrar todos os checkpoints
- **Clique em checkpoint:** Selecionar/mover checkpoint
- **Ctrl+Clique:** Adicionar novo checkpoint
- **Arrastar área vazia:** Mover câmera
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
       └── SeuMapa_checkpoints.json (crIAdo automaticamente)
   ```

2. **Adicione no config.py**:
   ```python
   "SeuMapa": {
       "nome": "Nome do Mapa",
       "arquivo_mapa": os.path.join(DIR_MAPS, "SeuMapa.png"),
       "arquivo_guIAs": os.path.join(DIR_MAPS_GUIDES, "SeuMapa_guides.png"),
       "arquivo_checkpoints": os.path.join(DIR_MAPS_GUIDES, "SeuMapa_checkpoints.json"),
       "waypoints_fallback": [(x1, y1), (x2, y2), ...]
   }
   ```

3. **Crie os checkpoints** usando o editor visual (F7)

### **Editor de Checkpoints**
- **Ative o modo edição** (F7)
- **Clique e arraste** para mover checkpoints
- **Clique em área vazIA** para adicionar novos
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
    "musica_aleatorIA": false
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
- **Sistema de Tração**: Traseira, frontal e integral com comportamentos únicos
- Aceleração e frenagem progressivas
- Sistema de derrapagem com contraesterço e colisões realistas
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
- **Documentado:** Documentação técnica completa disponível

### **Documentação para Desenvolvedores**
- **GDD:** Consulte o [Game Design Document](docs/gdd/GDD_Turbo_Racer.md) para entender o design do jogo
- **Game Objects:** Veja a [lista de objetos](docs/tech/GAME_OBJECTS_Turbo_Racer.md) para entender a arquitetura
- **API Reference:** Consulte a [documentação técnica](docs/tech/DOCUMENTACAO.md) para detalhes de implementação

### **Adicionando Novos Carros**
1. Adicione o sprite em `assets/images/cars/`
2. Configure em `CARROS_DISPONIVEIS` no `main.py`
3. Adicione sprite de seleção em `assets/images/car_selection/`
4. Consulte a documentação de Game Objects para detalhes técnicos

### **Personalizando Física**
- Ajuste constantes em `config.py`
- Modifique `core/carro.py` para física personalizada
- Configure parâmetros de IA em `core/ia.py`
- Veja exemplos na documentação técnica

### **Adicionando Novos Mapas**
- Siga o guia em [COMO_ADICIONAR_MAPAS.md](docs/guides/COMO_ADICIONAR_MAPAS.md)
- Use o editor visual de checkpoints (F7) para configurar navegação
- Consulte a documentação técnica para detalhes de implementação

---

## 🤝 Contribuição

### **Como Contribuir**
1. **Fork** o repositório
2. **Crie** uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. **Commit** suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. **Push** para a branch (`git push origin feature/nova-funcionalidade`)
5. **Abra** um Pull Request

### **Diretrizes de Contribuição**
- Siga a estrutura de código existente
- Mantenha a documentação atualizada
- Teste suas mudanças antes de submeter
- Use commits descritivos
- Consulte a documentação técnica antes de contribuir

### **Áreas de Contribuição**
- **Novos Carros:** Adicione sprites e configurações
- **Novos Mapas:** Crie pistas e checkpoints
- **MelhorIAs de IA:** Otimize algoritmos de navegação
- **Efeitos Visuais:** Adicione partículas e animações
- **Interface:** Melhore menus e HUD
- **Documentação:** Melhore guIAs e referêncIAs

---

## 📝 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.

---

## 📞 Suporte

- **Issues:** Use o sistema de issues do GitHub para reportar bugs
- **Documentação:** Consulte a documentação técnica para dúvidas
- **Desenvolvimento:** Veja os guIAs de contribuição para participar

---