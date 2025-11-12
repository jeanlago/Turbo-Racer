# Editor de Garagem - Turbo Racer

## Descrição

O **Garage Editor** é uma ferramenta visual para ajustar a posição, tamanho e escala dos carros na garagem/oficina do jogo. Similar ao editor de checkpoints, permite editar as propriedades dos carros de forma intuitiva.

## Como Usar

### Executar o Editor

```bash
python tools/garage_editor.py
```

### Controles

#### Navegação
- **← →**: Navegar entre carros
- **ESC**: Sair do editor

#### Modo Edição
- **F7**: Ativar/Desativar modo de edição
- **H**: Mostrar/Ocultar ajuda

#### Ajustes de Posição (Modo Edição)
- **W**: Mover para cima
- **S**: Mover para baixo
- **A**: Mover para esquerda
- **D**: Mover para direita

#### Ajustes de Tamanho (Modo Edição)
- **Q**: Diminuir largura
- **E**: Aumentar largura
- **Z**: Diminuir altura
- **X**: Aumentar altura

#### Mouse (Modo Edição)
- **Clique esquerdo**: Selecionar carro
- **Arrastar**: Mover carro
- **Arrastar cantos**: Redimensionar carro (cantos amarelos)

#### Salvar/Carregar
- **F5**: Salvar configurações em `data/garage_config.json`
- **F6**: Carregar configurações de `data/garage_config.json`

## Funcionalidades

### Visualização
- Mostra todos os carros na oficina
- Exibe fundo da oficina (se disponível)
- Carro selecionado destacado em verde
- Cantos de redimensionamento visíveis quando selecionado

### Edição
- **Posição da Oficina**: Ajusta onde o canvas do carro é desenhado na tela
- **Tamanho da Oficina**: Ajusta o tamanho do canvas (largura x altura)
- **Posição do Menu**: Pode ser ajustada (mas não visualizada no editor)

### Exportação
Ao salvar (F5), o editor:
1. Salva em `data/garage_config.json` (formato JSON)
2. Gera código Python no terminal para copiar diretamente no `main.py`

## Estrutura dos Dados

Cada carro possui:
- `posicao`: Posição na tela de seleção de carros (menu)
- `posicao_oficina`: Posição (x, y) onde o canvas é desenhado na oficina
- `tamanho_oficina`: Tamanho (largura, altura) do canvas na oficina

## Exemplo de Uso

1. Execute o editor: `python tools/garage_editor.py`
2. Pressione **F7** para ativar o modo edição
3. Use **← →** para selecionar o carro desejado
4. Arraste o carro para reposicioná-lo ou arraste os cantos para redimensionar
5. Pressione **F5** para salvar
6. Copie o código gerado no terminal e cole no `main.py` (lista `CARROS_DISPONIVEIS`)

## Notas

- O editor carrega os dados diretamente de `src/main.py` (lista `CARROS_DISPONIVEIS`)
- As alterações são salvas em JSON, mas o código gerado deve ser copiado manualmente para `main.py`
- O tamanho mínimo do canvas é 100x100 pixels
- Os sprites dos carros são carregados automaticamente de `assets/images/car_selection/` ou `assets/images/sprites/`

