# Como Adicionar Novos Mapas

## Sistema Escalável de Mapas Implementado ✅

O sistema agora suporta múltiplos mapas de forma escalável. Para adicionar um novo mapa, siga estes passos:

### 1. Preparar os Arquivos do Mapa

Coloque os arquivos do seu novo mapa na estrutura de pastas:

```
assets/images/maps/
├── Map_1.png                    # Mapa existente
├── Map_2.png                    # Seu novo mapa
└── guides/
    ├── Map_1_guides.png         # Guias do mapa existente
    ├── Map_1_checkpoints.json   # Checkpoints do mapa existente
    ├── Map_2_guides.png         # Guias do seu novo mapa
    └── Map_2_checkpoints.json   # Checkpoints do seu novo mapa (será criado automaticamente)
```

### 2. Adicionar o Mapa no Config

Edite o arquivo `src/config.py` e adicione seu mapa na seção `MAPAS_DISPONIVEIS`:

```python
MAPAS_DISPONIVEIS = {
    "Map_1": {
        "nome": "Pista Principal",
        "arquivo_mapa": os.path.join(DIR_MAPS, "Map_1.png"),
        "arquivo_guias": os.path.join(DIR_MAPS_GUIDES, "Map_1_guides.png"),
        "arquivo_checkpoints": os.path.join(DIR_MAPS_GUIDES, "Map_1_checkpoints.json"),
        "waypoints_fallback": [
            (820, 140), (930, 360), (860, 620),
            (520, 650), (200, 600), (160, 420),
            (260, 150), (500, 120)
        ]
    },
    "Map_2": {  # ← ADICIONE AQUI
        "nome": "Pista Secundária",
        "arquivo_mapa": os.path.join(DIR_MAPS, "Map_2.png"),
        "arquivo_guias": os.path.join(DIR_MAPS_GUIDES, "Map_2_guides.png"),
        "arquivo_checkpoints": os.path.join(DIR_MAPS_GUIDES, "Map_2_checkpoints.json"),
        "waypoints_fallback": [
            (100, 100), (200, 200), (300, 300),  # Pontos de fallback para IA
            (400, 400), (500, 500), (600, 600)
        ]
    }
}
```

### 3. Criar Checkpoints para o Novo Mapa

1. **Inicie o jogo** e vá para o menu
2. **Selecione "SELECIONAR MAPAS"** e escolha seu novo mapa
3. **Pressione F7** para entrar no modo de edição de checkpoints
4. **Clique e arraste** para criar e posicionar os checkpoints
5. **Pressione F5** para salvar os checkpoints
6. **Pressione F9** para alternar entre mapas durante a edição

### 4. Funcionalidades Disponíveis

#### No Menu:
- **SELECIONAR MAPAS**: Escolha qual mapa jogar
- Navegação com ↑ ↓
- ENTER para selecionar

#### Durante o Jogo (Modo Edição F7):
- **F5**: Salvar checkpoints do mapa atual
- **F6**: Carregar checkpoints do mapa atual
- **F7**: Ativar/desativar modo de edição
- **F8**: Limpar todos os checkpoints
- **F9**: Trocar para próximo mapa
- **Clique e Arrastar**: Mover checkpoints
- **Clique em área vazia**: Adicionar novo checkpoint
- **DEL**: Remover checkpoint selecionado

### 5. Estrutura dos Arquivos de Checkpoints

Os checkpoints são salvos automaticamente em formato JSON:

```json
[
  [541.0, 161.0],
  [203.0, 154.0],
  [157.0, 582.0],
  [445.0, 588.0]
]
```

### 6. Dicas para Criar Checkpoints Eficazes

1. **Posicione checkpoints** ao longo do caminho que a IA deve seguir
2. **Use pontos de referência** como curvas, retas e mudanças de direção
3. **Mantenha distância adequada** entre checkpoints (não muito próximos nem muito distantes)
4. **Teste a IA** após criar os checkpoints para verificar se está seguindo o caminho correto
5. **Ajuste conforme necessário** usando o modo de edição

### 7. Exemplo Completo

Para adicionar uma "Pista de Velocidade":

```python
"Speed_Track": {
    "nome": "Pista de Velocidade",
    "arquivo_mapa": os.path.join(DIR_MAPS, "Speed_Track.png"),
    "arquivo_guias": os.path.join(DIR_MAPS_GUIDES, "Speed_Track_guides.png"),
    "arquivo_checkpoints": os.path.join(DIR_MAPS_GUIDES, "Speed_Track_checkpoints.json"),
    "waypoints_fallback": [
        (100, 100), (300, 100), (500, 100),  # Reta inicial
        (700, 200), (800, 400), (700, 600),  # Curva
        (500, 700), (300, 700), (100, 600),  # Reta final
        (50, 400), (100, 200)                # Volta ao início
    ]
}
```

## ✅ Sistema Totalmente Escalável

- ✅ Suporte a múltiplos mapas
- ✅ Checkpoints independentes por mapa
- ✅ Interface de edição visual
- ✅ Arrastar e soltar checkpoints
- ✅ Troca de mapas em tempo real
- ✅ Salvamento automático
- ✅ Menu de seleção de mapas
- ✅ Fallback para IA quando não há checkpoints

Agora você pode facilmente adicionar quantos mapas quiser seguindo este processo!
