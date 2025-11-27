# Implementação do Sistema de Mapa da Cidade - Point and Click

## ✅ O que foi implementado:

### 1. Sistema de Territórios (`src/core/territorios.py`)
- Definição de 5 territórios principais:
  - **As Docas do Barão** (Dinheiro Rápido - Alto Risco)
  - **A Fábrica do Boris** (Peças Brutas - Sorte/Azar)
  - **O Templo da Akira** (Técnica - Melhorar Dirigibilidade)
  - **O Bueiro do Pixel** (Informação - Desbloqueios)
  - **A Torre Neon do Rex** (Progressão - História Principal)
- Sistema de tipos de territórios
- Sistema de atividades por território
- Funções auxiliares para buscar territórios

### 2. Tela do Mapa Isométrico (`src/core/mapa_cidade.py`)
- Interface point-and-click funcional
- Hover com tooltips informativos
- Visualização de territórios desbloqueados
- Cores diferentes por tipo de território
- Animações de hover pulsante
- Suporte para imagem de fundo (`mundo_aberto.png`)

### 3. Hub do Território (`src/core/hub_territorio.py`)
- Tela de ações após selecionar um território
- Exibição do NPC local (se existir sprite)
- Lista de atividades disponíveis
- Navegação por teclado e mouse
- Informações de risco/recompensa/custo
- Fundo personalizado por tipo de território

## 🔨 O que falta implementar:

### 4. Integração com a Garagem
- Adicionar botão "Abrir Mapa" na tela da oficina (`selecionar_carros_loop`)
- Modificar o retorno da função para permitir navegação para o mapa

### 5. Sistema de Transições
- Transição Garagem → Mapa
- Transição Mapa → Hub do Território
- Transição Hub → Corrida (usando sistema existente)
- Transição Corrida → Resultados → Garagem

### 6. Sistema de Atividades
- Implementar lógica para cada tipo de atividade:
  - `corrida_aposta`: Corrida com apostas altas
  - `loja_roleta`: Sistema de roleta de preços do Boris
  - `desafio_touge`: Desafio de montanha com penalidades
  - `informacao`: Sistema de compra de informações
  - `corrida_ranking`: Corridas principais do Rex

### 7. Integração com NPCs Existentes
- Conectar atividades com diálogos dos NPCs
- Usar sprites existentes dos NPCs nos hubs
- Integrar sistema de humor/estado dos NPCs

### 8. Sistema de Desbloqueio
- Desbloquear territórios baseado em progresso
- Salvar estado de desbloqueio no `progresso.json`

## 📝 Próximos Passos Sugeridos:

1. **Adicionar botão "Abrir Mapa" na oficina**
   - Modificar `selecionar_carros_loop` em `src/core/menu.py`
   - Adicionar botão visual no canto da tela
   - Chamar `mapa_cidade_loop` quando clicado

2. **Criar função de transição central**
   - Função que gerencia todas as transições entre telas
   - Efeitos visuais (fade in/out)

3. **Integrar com sistema de corridas existente**
   - Modificar `main.principal()` para aceitar atividades do mapa
   - Mapear atividades para parâmetros de corrida

4. **Adicionar persistência**
   - Salvar territórios desbloqueados em `progresso.json`
   - Carregar estado ao iniciar o jogo

## 🎨 Assets Necessários:

- [x] `mundo_aberto.png` (já existe em `assets/images/ui/`)
- [ ] Sprites de fundo para cada território (opcional)
- [ ] Efeitos de transição (opcional)

## 🔧 Como Testar:

1. Importar os módulos criados:
```python
from core.mapa_cidade import mapa_cidade_loop
from core.hub_territorio import hub_territorio_loop
from core.territorios import TERRITORIOS
```

2. Chamar o mapa da cidade:
```python
territorio_id = mapa_cidade_loop(screen)
if territorio_id:
    atividade = hub_territorio_loop(screen, territorio_id)
    if atividade:
        # Processar atividade (corrida, loja, etc.)
        pass
```

## 📚 Estrutura de Dados:

### Território:
```python
{
    "id": "docas_barao",
    "nome": "As Docas do Barão",
    "tipo": "dinheiro_rapido",
    "npc_id": "barao",
    "posicao_mapa": (200, 150),
    "area_clicavel": (180, 130, 120, 80),
    "atividades": [...]
}
```

### Atividade:
```python
{
    "tipo": "corrida_aposta",
    "nome": "Corrida de Aposta Alta",
    "risco": "alto",
    "recompensa": "alta"
}
```

