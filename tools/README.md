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

**Autor**: Turbo Racer Team  
**Versão**: 1.0  
**Data**: Janeiro 2025
