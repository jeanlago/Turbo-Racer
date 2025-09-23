# 🚗 Como Adicionar Carros - Turbo Racer

Guia passo a passo para adicionar novos carros ao Turbo Racer.

## 📋 Pré-requisitos

- Conhecimento básico de Python
- Editor de imagens (GIMP, Photoshop, etc.)
- Acesso aos arquivos do jogo

## 🎯 Passo a Passo

### 1. Preparar Assets

#### Sprites do Carro
- **Formato:** PNG com transparência
- **Resolução:** Recomendado 64x32 pixels
- **Orientação:** Carro apontando para a direita (0°)
- **Cores:** Use cores distintas para cada carro

#### Sprite de Seleção
- **Formato:** PNG com transparência
- **Resolução:** Recomendado 128x64 pixels
- **Orientação:** Carro apontando para a direita
- **Estilo:** Mais detalhado que o sprite do jogo

### 2. Configurar no Código

#### Adicionar ao `main.py`

```python
# Em CARROS_DISPONIVEIS
{
    "nome": "Nome do Carro",
    "prefixo_cor": "PrefixoCor",
    "tipo_tracao": "RWD",  # RWD, FWD, ou AWD
    "sprite_selecao": "PrefixoCor",
    "tamanho_oficina": (100, 60),  # Largura, Altura
    "posicao_oficina": (300, 150)  # X, Y
}
```

### 3. Tipos de Tração

#### RWD (Tração Traseira)
- **Características:** Pode fazer drift
- **Comportamento:** Instável em curvas
- **Ideal para:** Drift e corridas técnicas

#### FWD (Tração Frontal)
- **Características:** Não pode fazer drift
- **Comportamento:** Muito estável
- **Ideal para:** Corridas de velocidade

#### AWD (Tração Integral)
- **Características:** Drift limitado
- **Comportamento:** Equilibrado
- **Ideal para:** Corridas mistas

### 4. Configurar Física

#### Parâmetros Personalizados

```python
# Em carro_fisica.py, classe CarroFisica
def __init__(self, x, y, angulo, tipo_tracao="RWD"):
    # ... código existente ...
    
    # Parâmetros específicos por tipo
    if tipo_tracao == "RWD":
        self.grip_lateral = 0.7  # Menor grip = mais drift
        self.acel_base = 0.08
    elif tipo_tracao == "FWD":
        self.grip_lateral = 0.95  # Maior grip = mais estável
        self.acel_base = 0.09
    elif tipo_tracao == "AWD":
        self.grip_lateral = 0.8   # Grip médio
        self.acel_base = 0.085
```

### 5. Testar o Carro

1. **Executar** o jogo
2. **Selecionar** o novo carro
3. **Testar** física e controles
4. **Verificar** comportamento de drift
5. **Ajustar** parâmetros se necessário

## 🎨 Dicas de Design

### Sprites
- **Estilo consistente** com outros carros
- **Cores distintas** para fácil identificação
- **Detalhes apropriados** para a resolução
- **Transparência** para sobreposições

### Física
- **Balanceamento** - Não muito rápido/lento
- **Comportamento único** - Cada carro deve ser diferente
- **Teste extensivo** - Verificar em diferentes situações

### Seleção
- **Posicionamento** - Não sobrepor outros carros
- **Tamanho adequado** - Visível mas não muito grande
- **Informações** - Nome e especificações visíveis

## 🔧 Troubleshooting

### Problemas Comuns

**Carro não aparece:**
- Verificar caminhos dos arquivos
- Verificar formato das imagens
- Verificar configuração no main.py

**Física estranha:**
- Verificar tipo de tração
- Verificar parâmetros de física
- Testar com diferentes velocidades

**Drift não funciona:**
- Verificar se tipo_tracao != "FWD"
- Verificar parâmetros de grip
- Testar controles de drift

### Debug

- **F1** - Ativar debug da IA
- **H** - Alternar HUD completo
- **Teste manual** - Verificar comportamento

## 📁 Estrutura de Arquivos

```
assets/
├── images/
│   ├── cars/
│   │   └── PrefixoCor.png
│   └── car_selection/
│       └── PrefixoCor.png
```

## ✅ Checklist

- [ ] Sprites do carro criados
- [ ] Sprite de seleção criado
- [ ] Configuração adicionada ao main.py
- [ ] Tipo de tração definido
- [ ] Parâmetros de física ajustados
- [ ] Teste de física e controles
- [ ] Teste de drift (se aplicável)
- [ ] Teste de seleção na oficina
- [ ] Documentação atualizada

## 📊 Exemplo Completo

```python
# Configuração completa de um carro
{
    "nome": "Ferrari F40",
    "prefixo_cor": "FerrariF40",
    "tipo_tracao": "RWD",
    "sprite_selecao": "FerrariF40",
    "tamanho_oficina": (120, 70),
    "posicao_oficina": (400, 200)
}

# Parâmetros de física personalizados
if prefixo_cor == "FerrariF40":
    self.vel_max = 4.0      # Mais rápido
    self.acel_base = 0.1    # Aceleração maior
    self.grip_lateral = 0.6 # Menos grip = mais drift
```

---

**Próximo:** [Personalização](customization.md)  
**Voltar:** [Guia Principal](../README.md)
