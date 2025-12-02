# Relatório de Assets Faltantes para a Narrativa
## ✅ Backgrounds
**Todos os backgrounds estão disponíveis!** (17/17)
Todos os backgrounds necessários foram mapeados para arquivos existentes na pasta `assets/images/ui/`.
---

## ❌ Sprites Faltantes

- **Total de sprites necessários:** 34
- **Sprites existentes:** 16
- **Sprites faltantes:** 18

### Detalhamento por Personagem

#### CRANK (pasta: `mecanico/`)
**Status:** ❌ Pasta não existe

**Sprites necessários:**
- `crank_irritado.png` ❌
- `crank_neutro.png` ❌
- `crank_ranzinza.png` ❌
- `crank_sarcastico.png` ❌
- `crank_serio.png` ❌
- `crank_sobrancelha_levantada.png` ❌
- `crank_surpreso.png` ❌
- `crank_suspeita.png` ❌

**Sugestão de mapeamento:**
- `crank_irritado` → Criar novo sprite
- `crank_neutro` → Criar novo sprite
- `crank_ranzinza` → Criar novo sprite
- `crank_sarcastico` → Criar novo sprite
- `crank_serio` → Criar novo sprite
- `crank_sobrancelha_levantada` → Criar novo sprite
- `crank_surpreso` → Criar novo sprite
- `crank_suspeita` → Criar novo sprite

---

#### BORIS (pasta: `boris/`)
**Status:** ✅ Pasta existe

**Sprites necessários:**
- `boris_irritado_leve.png` → ✅ **Existe**
- `boris_neutro.png` → ✅ **Existe**
- `boris_sorriso.png` → ✅ **Existe**
- `boris_sorriso_malandro.png` → ✅ **Existe**
- `boris_suspeita.png` → ✅ **Existe**

**Sprites disponíveis (não usados na narrativa):**
- `boris_ameacador.png`
- `boris_apressado.png`
- `boris_oferta.png`
- `boris_oferta_2.png`
- `boris_persuasivo.png`

---

#### PIXEL (pasta: `pixel/`)
**Status:** ✅ Pasta existe

**Sprites necessários:**
- `pixel_assustado.png` → ✅ **Existe**
- `pixel_filosofico.png` → ✅ **Existe**
- `pixel_malandro.png` → ✅ **Existe**
- `pixel_malandro_triste.png` → ✅ **Existe**
- `pixel_neutro.png` → ✅ **Existe**
- `pixel_preocupado.png` → ✅ **Existe**
- `pixel_serio.png` → ✅ **Existe**
- `pixel_sorriso.png` → ✅ **Existe**

**Sprites disponíveis (não usados na narrativa):**
- `pixel_despedida.png`
- `pixel_silencio.png`
- `pixel_vendendo.png`

---

#### AKIRA (pasta: `akira/`)
**Status:** ✅ Pasta existe

**Sprites necessários:**
- `akira_neutra.png` → ✅ **Existe**
- `akira_seria.png` → ✅ **Existe**
- `akira_sorriso_sutil.png` → ✅ **Existe**

---

#### BARAO (pasta: `vendedor/`)
**Status:** ❌ Pasta não existe

**Sprites necessários:**
- `barao_inocente.png` ❌
- `barao_neutro.png` ❌
- `barao_sorriso_fino.png` ❌
- `barao_sorriso_largo.png` ❌

**Sugestão de mapeamento:**
- `barao_inocente` → Criar novo sprite
- `barao_neutro` → Criar novo sprite
- `barao_sorriso_fino` → Criar novo sprite
- `barao_sorriso_largo` → Criar novo sprite

---

#### REX (pasta: `rival/`)
**Status:** ❌ Pasta não existe

**Sprites necessários:**
- `rex_entediado.png` ❌
- `rex_holograma_neutro.png` ❌
- `rex_interessado.png` ❌
- `rex_neutro.png` ❌

**Sugestão de mapeamento:**
- `rex_entediado` → Criar novo sprite
- `rex_holograma_neutro` → Criar novo sprite
- `rex_interessado` → Criar novo sprite
- `rex_neutro` → Criar novo sprite

---

#### GLUB (pasta: `comprador/`)
**Status:** ❌ Pasta não existe

**Sprites necessários:**
- `glub_feliz.png` ❌

**Sugestão de mapeamento:**
- `glub_feliz` → Criar novo sprite

---

#### SLICK (pasta: `vendedor/`)
**Status:** ❌ Pasta não existe

**Sprites necessários:**
- `slick_sorriso_teatral.png` ❌

**Sugestão de mapeamento:**
- `slick_sorriso_teatral` → Criar novo sprite

---

## 📋 Ações Necessárias

### Opção 1: Criar Sprites Faltantes
Criar todos os sprites listados acima nas respectivas pastas.

### Opção 2: Mapear Sprites Existentes
Atualizar o sistema de narrativa para mapear os sprites necessários para os sprites existentes (usando os mapeamentos sugeridos acima).

### Opção 3: Renomear Sprites Existentes
Renomear os sprites existentes para corresponder aos nomes esperados pelo JSON.

---

## 🎯 Prioridade

1. **CRANK** - Alta prioridade (personagem principal)
2. **BORIS** - Alta prioridade (aparece no Capítulo 1)
3. **AKIRA** - Média prioridade (Capítulo 3)
4. **PIXEL** - Média prioridade (aparece em vários capítulos)
5. **BARAO** - Média prioridade (Capítulo 2)
6. **REX** - Baixa prioridade (Capítulos 4-5)
7. **GLUB** - Baixa prioridade (Capítulo 4)
8. **SLICK** - Baixa prioridade (Capítulo 4)

---

## 📝 Notas

- O sistema de narrativa já tem fallback para usar o primeiro sprite disponível se o sprite específico não existir
- Alguns sprites podem ser reutilizados com nomes diferentes
- O sistema pode ser atualizado para fazer mapeamento automático de nomes similares
