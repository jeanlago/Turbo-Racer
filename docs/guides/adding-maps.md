# 🗺️ Como Adicionar Mapas - Turbo Racer

Guia completo para adicionar novos mapas ao Turbo Racer usando o sistema de detecção automática.

## 📋 Pré-requisitos

- **Editor de imagens** (GIMP, Photoshop, Paint.NET, etc.)
- **Acesso aos arquivos** do jogo
- **Conhecimento básico** de design de pistas
- **NÃO é necessário conhecimento de Python!** ✅

## 🎯 Passo a Passo

### 1. Preparar Assets

#### **🗺️ Mapa Principal (OBRIGATÓRIO)**
- **Formato:** PNG com transparência
- **Resolução:** 
  - Mínimo: 1280x720
  - Recomendado: 1920x1080
  - Máximo: 2560x1440 (para performance)
- **Cores Padrão:**
  - **🟠 Laranja (255, 165, 0)** - Pista transitável
  - **🟢 Verde (0, 255, 0)** - Limites não transitáveis
  - **🟣 Magenta (255, 0, 255)** - Checkpoints/área transitável

#### **🎯 Guias de Navegação (OPCIONAL)**
- **Formato:** PNG com transparência
- **Resolução:** Mesma do mapa principal
- **Cores:**
  - **🟡 Amarelo (255, 255, 0)** - Linha de largada
  - **🔵 Azul (0, 0, 255)** - Guias de navegação

### 2. Adicionar Arquivos (ZERO CONFIGURAÇÃO)

#### **📁 Estrutura de Arquivos**
```
assets/images/maps/
├── MeuMapa.png                    # OBRIGATÓRIO
└── guides/
    ├── MeuMapa_guides.png         # OPCIONAL
    └── MeuMapa_checkpoints.json   # OPCIONAL (criado automaticamente)
```

#### **📝 Convenção de Nomes**
- **Arquivo principal:** `NomeDoMapa.png`
- **Guias:** `NomeDoMapa_guides.png`
- **Checkpoints:** `NomeDoMapa_checkpoints.json`

#### **✨ Nomes Inteligentes**
O sistema converte automaticamente:
- `MeuMapa` → "Meu Mapa"
- `Pista_Circuito` → "Pista Circuito"
- `Mapa_Teste_01` → "Mapa Teste 01"

### 3. Ativar o Mapa (AUTOMÁTICO)

1. **🚀 Executar** o jogo
2. **📋 Ir para "Selecionar Mapas"**
3. **🔄 Pressionar R** para recarregar mapas (se necessário)
4. **✅ Selecionar** o novo mapa na lista

### 4. Criar Checkpoints (OPCIONAL)

#### **✏️ Usando o Editor Visual**
1. **🎮 Entrar** no mapa
2. **⌨️ Pressionar F7** para entrar no modo edição
3. **🖱️ Posicionar** checkpoints clicando na pista
4. **🔄 Mover** checkpoints arrastando
5. **💾 Pressionar F5** para salvar

#### **🎯 Dicas de Posicionamento**
- **Coloque checkpoints** em curvas importantes
- **Mantenha distância** adequada entre eles
- **Evite áreas** muito estreitas
- **Teste a navegação** da IA (F1 para debug)

### 5. Testar o Mapa

1. **🎮 Executar** o jogo
2. **🗺️ Selecionar** o novo mapa
3. **🤖 Testar** navegação da IA (F1 para debug)
4. **✅ Verificar** checkpoints
5. **🔧 Ajustar** se necessário

## 🚀 Vantagens do Sistema Escalável

- ✅ **Zero configuração manual** - apenas coloque os arquivos
- ✅ **Detecção automática** - mapas aparecem automaticamente
- ✅ **Nomes inteligentes** - "MeuMapa" vira "Meu Mapa"
- ✅ **Fallback robusto** - funciona mesmo sem guias/checkpoints
- ✅ **Recarregamento dinâmico** - adicione mapas sem reiniciar

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
