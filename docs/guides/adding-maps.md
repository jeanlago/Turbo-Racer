# 🗺️ Como Adicionar Pistas GRIP - Turbo Racer

**⚠️ IMPORTANTE:** A partir da versão 3.1.0, o Turbo Racer utiliza **exclusivamente** o sistema de pistas GRIP com tiles dinâmicos. O sistema antigo de mapas baseado em imagens PNG foi removido.

Guia completo para adicionar novas pistas GRIP ao Turbo Racer.

## 📋 Pré-requisitos

- **Editor de imagens** (GIMP, Photoshop, Paint.NET, etc.) para criar tiles
- **Acesso aos arquivos** do jogo
- **Conhecimento básico** de Python (para editar código)
- **Tiles do GRIP** - Arquivos de tiles de pista (b-x-x.png, st-h-3-*.png, etc.)

## 🎯 Passo a Passo

### 1. Preparar Tiles

#### **📁 Estrutura de Tiles**
```
assets/images/pistas/
├── b-x-x.png              # Tiles de pista (vários)
├── st-h-3-ch.png          # Linha de largada/chegada
├── st-h-3-kX.png          # Tiles de pista horizontais
├── st-v-3-kX.png          # Tiles de pista verticais
├── overhead_tile.png      # Tile de grama (fundo)
└── trackX.png             # Minimapa da pista (1-9)
```

### 2. Definir Layout da Pista

#### **📝 Editar `src/core/pista_tiles.py`**

Adicione um novo método `_definicao_pista_X()` (onde X é o número da pista):

```python
def _definicao_pista_10(self):
    """Definição da Pista 10"""
    self.numero_pista = 10
    self.posicao_inicial_relativa = (0, -50)  # Posição inicial do carro
    
    # Lista de tiles: (tipo_tile, offset_x, offset_y)
    self.tiles = [
        ("st-h-3-ch", 0, -50),      # Linha de largada
        ("b-x-x", 300, -50),        # Pista continua
        # ... adicione mais tiles
    ]
```

### 3. Adicionar Checkpoints

#### **📝 Editar `src/core/laps_grip.py`**

Adicione checkpoints na função `carregar_checkpoints_grip()`:

```python
if numero_pista == 10:
    centro_x, centro_y = 2500, 2500
    checkpoint_1 = (centro_x + 0, centro_y + -50, 90)  # (x, y, angulo)
    checkpoint_2 = (centro_x + 300, centro_y + -50, 90)
    # ... adicione mais checkpoints
    
    checkpoints = [
        checkpoint_1,
        checkpoint_2,
        # ...
    ]
```

### 4. Usar o Editor Visual

#### **✏️ Editor de Checkpoints e Spawn Points**

1. **🚀 Executar** `python tools/checkpoint_editor.py`
2. **⌨️ Pressionar F9** ou setas para selecionar a pista
3. **⌨️ Pressionar F7** para ativar modo edição
4. **🖱️ Clique** para adicionar checkpoints
5. **🔄 Arraste** para mover checkpoints
6. **⌨️ R/Q/E** para rotacionar checkpoints selecionados
7. **⌨️ Shift+F7** para alternar modo spawn points
8. **⌨️ F10** para exportar para `laps_grip.py`
9. **⌨️ F5** para salvar backup em JSON

### 5. Adicionar Minimapa

#### **🖼️ Criar Minimapa**

1. **Criar** imagem `track10.png` (exemplo: 200x200px)
2. **Colocar** em `assets/images/pistas/`
3. **O minimapa** será carregado automaticamente

### 6. Testar a Pista

1. **🎮 Executar** o jogo
2. **🗺️ Selecionar** a nova pista na tela de seleção de fase
3. **🤖 Testar** navegação da IA (F1 para debug)
4. **✅ Verificar** checkpoints e spawn points
5. **🔧 Ajustar** se necessário

## 🎨 Dicas de Design

### Layout da Pista
- **Use tiles existentes** - Reutilize tiles do GRIP
- **Curvas suaves** - Combine tiles horizontais e verticais
- **Largura adequada** - Pista deve acomodar múltiplos carros
- **Checkpoints estratégicos** - Posicione em curvas importantes

### Checkpoints
- **Perpendiculares à pista** - Use rotação (R, Q, E) para alinhar
- **Largura de 300px** - Mesma largura dos tiles de pista
- **Distância adequada** - Não muito próximos nem muito distantes

### Spawn Points
- **Múltiplos pontos** - Defina 4+ pontos para variedade
- **Na linha de largada** - Posicione na área de largada
- **Lado a lado** - Para permitir largada simultânea

## 🔧 Troubleshooting

### Problemas Comuns

**Tiles não aparecem:**
- Verificar se arquivos estão em `assets/images/pistas/`
- Verificar nomes dos arquivos (case-sensitive)
- Verificar definição em `pista_tiles.py`

**Checkpoints não funcionam:**
- Verificar se foram exportados para `laps_grip.py` (F10)
- Verificar formato (x, y, angulo)
- Testar com editor visual

**IA não segue checkpoints:**
- Verificar se checkpoints estão na ordem correta
- Verificar se ângulos estão corretos
- Usar F1 para debug visual

### Debug

- **F1** - Ativar debug da IA (no jogo)
- **F7** - Modo edição de checkpoints (no editor)
- **F9** - Trocar de pista (no editor)
- **F10** - Exportar checkpoints para `laps_grip.py`

## 📁 Estrutura de Arquivos

```
assets/images/pistas/
├── b-x-x.png              # Tiles de pista
├── st-h-3-ch.png          # Linha de largada
├── overhead_tile.png      # Tile de grama
└── trackX.png             # Minimapas (1-9)

src/core/
├── pista_tiles.py         # Definições de pistas
└── laps_grip.py            # Checkpoints e spawn points

data/
└── checkpoints_pista_X.json # Backup de checkpoints
```

## ✅ Checklist

- [ ] Tiles criados/obtidos
- [ ] Layout definido em `pista_tiles.py`
- [ ] Checkpoints adicionados em `laps_grip.py`
- [ ] Spawn points definidos
- [ ] Minimapa criado (`trackX.png`)
- [ ] Teste de navegação da IA
- [ ] Teste de checkpoints
- [ ] Teste de spawn points
- [ ] Exportação para `laps_grip.py` (F10)

---

**Próximo:** [Como Adicionar Carros](adding-cars.md)  
**Voltar:** [Guia Principal](../README.md)
