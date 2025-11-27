# Sistema de Tradução para Narrativa

## Status Atual

✅ **Sistema de tradução integrado** - O sistema de narrativa agora suporta tradução através do sistema i18n existente.

⚠️ **Textos ainda não traduzidos** - Os textos no `data/narrative.json` estão em português e precisam ser migrados para chaves de tradução.

## Como Funciona

### 1. Sistema de Tradução

O sistema de narrativa agora verifica se um texto começa com `"narrative."`. Se sim, ele usa a função `t()` para traduzir:

```json
{
  "speaker": "CRANK",
  "text": "narrative.ch1.crank.garage.intro.line1"
}
```

### 2. Estrutura de Tradução

As traduções devem ser adicionadas nos arquivos `data/locales/{idioma}.json` na seção `"narrative"`:

```json
{
  "narrative": {
    "narrator": "NARRADOR",
    "system": "SISTEMA",
    "press_to_continue": "Pressione ESPAÇO ou clique para continuar",
    "characters": {
      "crank": "CRANK",
      "boris": "BORIS",
      "pixel": "PIXEL",
      "akira": "AKIRA",
      "barao": "BARÃO",
      "rex": "REX",
      "glub": "GLUB",
      "slick": "SLICK"
    },
    "ch1": {
      "crank": {
        "garage": {
          "intro": {
            "line1": "…Mas que porcaria é essa debaixo do capô?",
            "line2": "Eu fui trocar o filtro de óleo..."
          }
        }
      }
    }
  }
}
```

## Migração dos Textos

### Opção 1: Manter Textos Diretos (Atual)

Os textos podem permanecer diretos no JSON. O sistema funcionará, mas não será traduzido:

```json
{
  "speaker": "CRANK",
  "text": "…Mas que porcaria é essa debaixo do capô?"
}
```

### Opção 2: Usar Chaves de Tradução (Recomendado)

Migrar os textos para chaves de tradução:

1. **No `narrative.json`**, substituir textos por chaves:
```json
{
  "speaker": "CRANK",
  "text": "narrative.ch1.crank.garage.intro.line1"
}
```

2. **Nos arquivos de locale**, adicionar as traduções:
   - `data/locales/pt.json` - Português
   - `data/locales/en.json` - Inglês
   - `data/locales/es.json` - Espanhol
   - `data/locales/fr.json` - Francês

## Estrutura Sugerida para Traduções

```
narrative.
  ├── narrator (já traduzido)
  ├── system (já traduzido)
  ├── press_to_continue (já traduzido)
  ├── characters (já traduzido)
  └── ch1 (capítulo 1)
      ├── prologue
      │   ├── line1
      │   ├── line2
      │   └── line3
      ├── crank
      │   └── garage
      │       ├── intro
      │       │   ├── line1
      │       │   ├── line2
      │       │   └── line3
      │       └── choices
      │           ├── choice1
      │           ├── choice2
      │           └── choice3
      └── ...
  └── ch2 (capítulo 2)
      └── ...
```

## Exemplo Completo

### narrative.json
```json
{
  "lines": [
    {
      "speaker": "CRANK",
      "text": "narrative.ch1.crank.garage.intro.line1"
    }
  ],
  "choices": [
    {
      "text": "narrative.ch1.crank.garage.choices.choice1"
    }
  ]
}
```

### pt.json
```json
{
  "narrative": {
    "ch1": {
      "crank": {
        "garage": {
          "intro": {
            "line1": "…Mas que porcaria é essa debaixo do capô?"
          },
          "choices": {
            "choice1": "Quero correr."
          }
        }
      }
    }
  }
}
```

### en.json
```json
{
  "narrative": {
    "ch1": {
      "crank": {
        "garage": {
          "intro": {
            "line1": "...What the hell is this under the hood?"
          },
          "choices": {
            "choice1": "I want to race."
          }
        }
      }
    }
  }
}
```

## Status da Tradução

### ✅ Já Traduzido
- Nomes dos personagens
- "NARRADOR" / "NARRATOR"
- "SISTEMA" / "SYSTEM"
- "Pressione ESPAÇO ou clique para continuar"

### ❌ Ainda Não Traduzido
- Todos os diálogos da narrativa (textos diretos no JSON)
- Todas as escolhas (textos diretos no JSON)

## Próximos Passos

1. **Decidir estratégia**: Manter textos diretos ou migrar para chaves?
2. **Se migrar**: Criar script para extrair textos e gerar estrutura de tradução
3. **Adicionar traduções**: Traduzir todos os textos para EN, ES, FR
4. **Atualizar JSON**: Substituir textos por chaves no `narrative.json`

## Nota

O sistema atual funciona com textos diretos. A tradução é opcional e pode ser adicionada gradualmente conforme necessário.

