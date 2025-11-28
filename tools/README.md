# Ferramentas - Turbo Racer

Esta pasta contém ferramentas auxiliares para o desenvolvimento e configuração do jogo Turbo Racer.

## Checkpoint Editor

### Descrição
Ferramenta independente para editar, criar e remover checkpoints de forma visual e intuitiva. Útil para configurar novos mapas ou ajustar checkpoints existentes sem precisar executar o jogo principal.

### Como Usar

#### Execução
```bash
# Na pasta raiz do projeto
python tools/checkpoint_editor.py
```

#### Controles

**Teclado:**
- `F7`: Ativar/Desativar modo de edição
- `F5`: Salvar checkpoints no arquivo
- `F6`: Recarregar checkpoints do arquivo
- `F8`: Limpar todos os checkpoints
- `F9`: Trocar para outro mapa
- `H`: Mostrar/Ocultar ajuda detalhada
- `ESC`: Sair do editor

**Mouse:**
- **Clique esquerdo**: Adicionar novo checkpoint (modo edição ativo)
- **Clique direito**: Remover checkpoint mais próximo (modo edição ativo)
- **Arrastar**: Mover checkpoint selecionado (modo edição ativo)
- **Arrastar**: Mover câmera (modo edição inativo)

### Funcionalidades

#### Modo de Edição
- **Ativo**: Permite adicionar, remover e mover checkpoints
- **Inativo**: Permite apenas navegar pela câmera

#### Gerenciamento de Checkpoints
- **Adicionar**: Clique esquerdo em qualquer lugar da pista
- **Remover**: Clique direito no checkpoint desejado
- **Mover**: Arraste o checkpoint para nova posição
- **Visualizar**: Checkpoints são numerados sequencialmente

#### Troca de Mapas
- Pressione `F9` para abrir menu de seleção
- Digite o número do mapa desejado
- Checkpoints são salvos automaticamente antes da troca

#### Salvamento Automático
- Checkpoints são salvos automaticamente ao sair
- Use `F5` para salvar manualmente
- Use `F6` para recarregar do arquivo

### Interface

#### Painel Principal
- **Título**: Nome da ferramenta
- **Mapa Atual**: Nome do mapa sendo editado
- **Modo Edição**: Status ativo/inativo
- **Contador**: Número total de checkpoints
- **Controles**: Lista de teclas disponíveis

#### Painel de Ajuda (H)
- **Instruções detalhadas** de uso
- **Explicação dos controles** do mouse
- **Dicas de navegação**

### Arquivos

#### Checkpoints Salvos
- **Localização**: `data/checkpoints_[mapa].json`
- **Formato**: JSON com array de coordenadas `[x, y]`
- **Exemplo**: `[[640, 360], [800, 200], [400, 500]]`

#### Mapas Suportados
- Todos os mapas disponíveis em `MAPAS_DISPONIVEIS`
- Carregamento automático de guias e máscaras
- Suporte a múltiplos mapas simultaneamente

### Dicas de Uso

#### Posicionamento de Checkpoints
- **Coloque em locais estratégicos** da pista
- **Evite áreas muito próximas** das bordas
- **Considere a dificuldade** da curva
- **Teste no jogo** após editar

#### Navegação
- **Use o mouse** para navegar pela pista
- **Arraste para mover** a câmera
- **Zoom automático** baseado na velocidade

#### Troubleshooting
- **Checkpoints não aparecem**: Verifique se o modo edição está ativo (F7)
- **Não consegue salvar**: Verifique permissões da pasta `data/`
- **Mapa não carrega**: Verifique se o mapa existe em `MAPAS_DISPONIVEIS`

### Exemplo de Uso

1. **Execute a ferramenta**:
   ```bash
   python tools/checkpoint_editor.py
   ```

2. **Ative o modo edição**:
   - Pressione `F7`

3. **Adicione checkpoints**:
   - Clique esquerdo em pontos estratégicos da pista

4. **Ajuste posições**:
   - Arraste checkpoints para posições ideais

5. **Salve as alterações**:
   - Pressione `F5` ou saia com `ESC`

6. **Teste no jogo**:
   - Execute o jogo principal para verificar os checkpoints

### Desenvolvimento

#### Estrutura do Código
- **Classe principal**: `CheckpointEditor`
- **Métodos principais**: `executar()`, `processar_eventos()`, `desenhar()`
- **Integração**: Usa módulos do jogo principal (`config`, `camera`, `pista`)

#### Extensões Possíveis
- **Importação/Exportação** de checkpoints
- **Validação automática** de posicionamento
- **Preview em tempo real** da IA
- **Estatísticas** de dificuldade

---

## Teste de Narrativa por Capítulo

### Descrição
Ferramenta para testar cada capítulo da narrativa sem precisar reiniciar o save. Permite selecionar qualquer capítulo e automaticamente configura o progresso do jogo para o estado apropriado.

### Como Usar

#### Execução
```bash
# Na pasta raiz do projeto
python tools/test_narrative.py
```

#### Controles
- **↑↓** ou **W/S**: Navegar entre capítulos
- **ENTER** ou **SPACE**: Selecionar capítulo
- **ESC**: Cancelar e sair

#### Capítulos Disponíveis
1. **Capítulo 1** - Ferrugem e Primeira Corrida
   - Prologue → Crank → Teste → Boris → Primeira Corrida
2. **Capítulo 2** - Contrato com o Barão
   - Barão → Empréstimo → Cinturão Industrial
3. **Capítulo 3** - Fluxo da Montanha
   - Akira → Montanha → Teste de Fluxo
4. **Capítulo 4** - Olhos nas Torres
   - Rex observa → Slick → Glub
5. **Capítulo 5** - Jogo do Rei
   - Circuito da Coroa → Preparações → Corrida Final

### Funcionalidades
- **Configuração automática**: O teste prepara o progresso (dinheiro, carros, flags de NPCs) automaticamente
- **Sem reiniciar save**: Não precisa deletar o progresso.json para testar diferentes capítulos
- **Menu visual**: Interface simples para seleção de capítulo
- **Integração completa**: Usa o sistema de narrativa real do jogo

---

## Editor de Cenários (scenario_editor.py)

### Descrição
Ferramenta visual para definir hitboxes clicáveis com hover em cenários do jogo. Permite criar áreas interativas que exibem sprites de hover quando o mouse passa sobre elas.

### Como Usar

#### Execução
```bash
# Na pasta raiz do projeto
python tools/scenario_editor.py
```

#### Controles

**Teclado:**
- `C` - Carregar cenário (seleciona de uma lista de cenários disponíveis)
- `N` - Criar nova hitbox
- `T` - Editar nome da hitbox selecionada
- `H` - Editar sprite de hover (lista sprites de `assets/images/hover/`)
- `A` - Editar ação (opcional, para definir ação ao clicar)
- `DELETE` - Remover hitbox selecionada
- `CTRL+S` - Salvar hitboxes
- `ESC` - Desselecionar hitbox

**Mouse:**
- **Clique esquerdo**: Criar nova hitbox (modo criar) ou selecionar/arrastar hitbox
- **Arrastar**: Mover hitbox selecionada
- **Cantos**: Clicar e arrastar nos cantos para redimensionar hitbox
- **Hover**: Visualização em tempo real de qual hitbox está sob o mouse

### Funcionalidades

#### Gerenciamento de Cenários
- **Carregar cenários**: Lista todos os arquivos PNG/JPG da pasta `assets/images/ui/`
- **Visualização**: Cenário é exibido centralizado e escalado para caber na tela
- **Múltiplos cenários**: Cada cenário tem suas próprias hitboxes salvas separadamente

#### Criação de Hitboxes
- **Criar**: Pressione `N` e clique onde deseja criar a hitbox
- **Mover**: Arraste a hitbox para reposicionar
- **Redimensionar**: Clique e arraste nos cantos (indicados por círculos brancos)
- **Visual**: Hitboxes são exibidas com overlay semi-transparente

#### Sprites de Hover
- **Associar**: Pressione `H` na hitbox selecionada para escolher um sprite
- **Origem**: Sprites são carregados de `assets/images/hover/` (incluindo subpastas como `casa/`, `mapa/`, `rex/`)
- **Caminho relativo**: Sprites são salvos com caminho relativo (`assets/images/hover/...`)

#### Ações
- **Definir ação**: Pressione `A` para definir uma ação opcional
- **Uso**: Pode ser usado para definir comportamentos ao clicar na hitbox (ex: "abrir_menu", "mostrar_dialogo")

### Arquivos

#### Hitboxes Salvos
- **Localização**: `data/scenario_hitboxes.json`
- **Formato**: JSON organizado por cenário
- **Estrutura**:
```json
{
  "casa.png": [
    {
      "id": "cafe",
      "nome": "Café",
      "x": 100,
      "y": 200,
      "largura": 150,
      "altura": 100,
      "hover_sprite": "assets/images/hover/casa/casa_cafe.png",
      "acao": "tomar_cafe"
    }
  ]
}
```

### Exemplo de Uso

1. **Execute a ferramenta**:
   ```bash
   python tools/scenario_editor.py
   ```

2. **Carregue um cenário**:
   - Pressione `C`
   - Escolha o número do cenário (ex: `casa.png`)

3. **Crie hitboxes**:
   - Pressione `N`
   - Clique onde deseja criar a hitbox
   - Arraste para mover, arraste cantos para redimensionar

4. **Associe sprites de hover**:
   - Selecione uma hitbox
   - Pressione `H`
   - Escolha o sprite de hover (ex: `casa/casa_cafe.png`)

5. **Salve**:
   - Pressione `CTRL+S` ou feche o editor (salva automaticamente)

### Integração com o Jogo

As hitboxes salvas podem ser carregadas no sistema de narrativa ou em outros sistemas do jogo para:
- Exibir sprites de hover quando o mouse passa sobre áreas clicáveis
- Detectar cliques em áreas específicas do cenário
- Executar ações personalizadas baseadas na hitbox clicada

---

**Autor**: Turbo Racer Team  
**Versão**: 1.0  
**Data**: Janeiro 2025
