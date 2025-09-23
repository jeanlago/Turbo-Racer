# 🗺️ Como Adicionar Mapas - Turbo Racer

Guia passo a passo para adicionar novos mapas ao Turbo Racer.

## 📋 Pré-requisitos

- Conhecimento básico de Python
- Editor de imagens (GIMP, Photoshop, etc.)
- Acesso aos arquivos do jogo

## 🎯 Passo a Passo

### 1. Preparar Assets

#### Mapa Principal
- **Formato:** PNG com transparência
- **Resolução:** Recomendado 1920x1080 ou superior
- **Cores:**
  - **Verde (0, 255, 0)** - Limite da pista (não transitável)
  - **Laranja (255, 165, 0)** - Pista válida
  - **Magenta (255, 0, 255)** - Checkpoints/área transitável

#### Guias de Navegação
- **Formato:** PNG com transparência
- **Resolução:** Mesma do mapa principal
- **Cores:**
  - **Amarelo (255, 255, 0)** - Linha de largada
  - **Azul (0, 0, 255)** - Guias de navegação

### 2. Configurar no Código

#### Adicionar ao `config.py`

```python
# Em MAPAS_DISPONIVEIS
"Mapa_Novo": {
    "nome": "Nome Exibido",
    "arquivo_mapa": os.path.join(DIR_MAPS, "Mapa_Novo.png"),
    "arquivo_guias": os.path.join(DIR_MAPS_GUIDES, "Mapa_Novo_guides.png"),
    "arquivo_checkpoints": os.path.join(DIR_MAPS_GUIDES, "Mapa_Novo_checkpoints.json"),
    "waypoints_fallback": [(x1, y1), (x2, y2), ...]  # Pontos de fallback
}
```

### 3. Criar Checkpoints

#### Usando o Editor Visual
1. **Executar** o jogo
2. **Pressionar F7** para entrar no modo edição
3. **Posicionar** checkpoints clicando na pista
4. **Mover** checkpoints arrastando
5. **Pressionar F5** para salvar

#### Programaticamente
```python
checkpoints = [
    (100, 100),  # Checkpoint 1
    (200, 200),  # Checkpoint 2
    (300, 300),  # Checkpoint 3
    # ... mais checkpoints
]

# Salvar
import json
with open("Mapa_Novo_checkpoints.json", "w") as f:
    json.dump(checkpoints, f)
```

### 4. Testar o Mapa

1. **Executar** o jogo
2. **Selecionar** o novo mapa
3. **Testar** navegação da IA
4. **Verificar** checkpoints
5. **Ajustar** se necessário

## 🎨 Dicas de Design

### Layout da Pista
- **Curvas suaves** - Evite ângulos muito fechados
- **Largura adequada** - Pista deve acomodar 2 carros
- **Obstáculos** - Use verde para criar desafios
- **Checkpoints** - Posicione em pontos estratégicos

### Cores e Contraste
- **Alto contraste** entre pista e limites
- **Cores consistentes** com o padrão do jogo
- **Transparência** para sobreposições

### Performance
- **Resolução otimizada** - Não muito alta
- **Áreas simples** - Evite detalhes desnecessários
- **Teste de performance** - Verificar FPS

## 🔧 Troubleshooting

### Problemas Comuns

**IA não segue o mapa:**
- Verificar cores das guias
- Verificar se arquivo de guias existe
- Usar fallback waypoints

**Checkpoints não funcionam:**
- Verificar formato JSON
- Verificar posições válidas
- Testar com F1 (debug)

**Mapa não aparece:**
- Verificar caminhos dos arquivos
- Verificar formato das imagens
- Verificar configuração no config.py

### Debug

- **F1** - Ativar debug da IA
- **F7** - Modo edição de checkpoints
- **F9** - Próximo mapa
- **F10** - Mostrar todos os checkpoints

## 📁 Estrutura de Arquivos

```
assets/
├── maps/
│   └── Mapa_Novo.png
└── maps_guides/
    ├── Mapa_Novo_guides.png
    └── Mapa_Novo_checkpoints.json
```

## ✅ Checklist

- [ ] Mapa principal criado
- [ ] Guias de navegação criadas
- [ ] Configuração adicionada ao config.py
- [ ] Checkpoints posicionados
- [ ] Teste de navegação da IA
- [ ] Teste de performance
- [ ] Documentação atualizada

---

**Próximo:** [Como Adicionar Carros](adding-cars.md)  
**Voltar:** [Guia Principal](../README.md)
