# Editor de Áreas do Mapa da Cidade

Ferramenta para definir áreas clicáveis e acessíveis no mapa isométrico da cidade.

## Como Usar

1. **Executar o editor:**
   ```bash
   python tools/mapa_editor.py
   ```

2. **Criar uma nova área:**
   - Pressione `N` para entrar no modo de criação
   - Clique no mapa onde deseja criar a área
   - A área será criada com tamanho padrão (120x80)

3. **Selecionar uma área:**
   - Clique na área desejada

4. **Mover uma área:**
   - Selecione a área
   - Arraste com o mouse

5. **Redimensionar uma área:**
   - Selecione a área
   - Clique e arraste um dos cantos (pequenos círculos)

6. **Editar nome da área:**
   - Selecione a área
   - Pressione `T`
   - Digite o novo nome no terminal

7. **Editar sprite de fundo:**
   - Selecione a área
   - Pressione `F`
   - Escolha um sprite disponível (1-5)
   - O sprite será exibido quando o jogador clicar na área

8. **Editar territorio_id:**
   - Selecione a área
   - Pressione `R`
   - Digite o ID do território correspondente (ex: "docas_barao", "oficina")
   - Isso mapeia a área para um território em `territorios.py`

9. **Remover uma área:**
   - Selecione a área
   - Pressione `DELETE`

10. **Salvar:**
    - Pressione `CTRL+S` para salvar
    - As áreas são salvas automaticamente ao fechar o editor

11. **Desselecionar:**
    - Pressione `ESC`

## Estrutura do Arquivo JSON

As áreas são salvas em `data/mapa_areas.json`:

```json
{
  "areas": [
    {
      "id": "oficina",
      "nome": "Oficina",
      "x": 200,
      "y": 150,
      "largura": 120,
      "altura": 80,
      "desbloqueada": true,
      "sprite_fundo": "assets/images/ui/oficina.png",
      "territorio_id": "oficina"
    }
  ]
}
```

## Campos

- **id**: Identificador único da área (usado para mapear com territórios)
- **nome**: Nome exibido no mapa
- **x, y**: Posição no mapa (coordenadas da imagem original)
- **largura, altura**: Tamanho da área clicável
- **desbloqueada**: Se a área está acessível (true/false)
- **sprite_fundo**: (Opcional) Caminho relativo do sprite de fundo (ex: "assets/images/ui/oficina.png")
- **territorio_id**: (Opcional) ID do território correspondente em `territorios.py`

## Integração com o Jogo

O jogo carrega automaticamente as áreas de `data/mapa_areas.json` quando o mapa da cidade é aberto. As áreas são mapeadas para territórios através do campo `territorio_id` ou pelo `id` da área.

## Dicas

- Use nomes descritivos para facilitar a identificação
- Certifique-se de que as áreas não se sobreponham muito
- Teste as áreas no jogo após salvar
- O mapa é escalado automaticamente para caber na tela, mas as coordenadas são da imagem original

