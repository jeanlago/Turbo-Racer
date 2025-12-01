# Organização das Missões - Turbo Racer

## Fluxo de Missões do Capítulo 1

### Sequência Principal:

1. **m1_primeira_faisca** (Primeira Faísca)
   - **Ativa em**: `ch1_0_prologue` (primeira cutscene)
   - **Objetivo**: Encontre a garagem do Crank no bairro baixo.
   - **Completa em**: `ch1_1_crank_garage_intro` (quando encontra o Crank)

2. **m2_teste_de_sobrevivencia** (Teste de Sobrevivência)
   - **Ativa em**: `ch1_1b_crank_test_briefing` (após encontrar Crank)
   - **Objetivo**: Complete a corrida de teste da garagem do Crank.
   - **Completa em**: `ch1_1c_crank_test_result` (após completar corrida de teste)

3. **m3_rota_da_ferrugem** (Rota da Ferrugem)
   - **Ativa em**: `ch1_1c_crank_test_result` (após teste)
   - **Objetivo**: Vá até o Fosso de Ferrugem e fale com Boris.
   - **Completa em**: `ch1_3_meet_boris` (quando encontra Boris)

4. **m4_coracao_de_sucata** (Coração de Sucata)
   - **Ativa em**: `ch1_3_meet_boris` (quando encontra Boris)
   - **Objetivo**: Compre uma peça principal com Boris para melhorar seu carro.
   - **Completa em**: **Automaticamente quando o jogador compra uma peça do Boris** (implementado em `boris.py`)

5. **m5_cirurgia_na_garagem** (Cirurgia na Garagem)
   - **Ativa em**: `ch1_4_return_garage_upgrade` (após comprar do Boris)
   - **Objetivo**: Volte à garagem do Crank e instale a nova peça.
   - **Completa em**: **Automaticamente quando o jogador instala um upgrade na garagem** (implementado em `menu.py`)

6. **m6_batismo_de_pista** (Batismo de Pista)
   - **Ativa em**: `ch1_5_first_race_unlocked` (após instalar upgrade)
   - **Objetivo**: Corra no Circuito de Treino e termine a corrida.
   - **Completa em**: `ch1_6_post_first_race_and_pixel` (após completar corrida)

7. **m7_olhos_no_painel** (Olhos no Painel)
   - **Ativa em**: `ch1_6_post_first_race_and_pixel` (após primeira corrida)
   - **Objetivo**: Ouça o que Pixel tem a dizer sobre seu desempenho.
   - **Completa em**: `ch1_7_pixel_intro` (quando Pixel aparece)

## O que fazer após visitar o Boris?

Após visitar o Boris e completar a missão **m3_rota_da_ferrugem**:

1. **Comprar uma peça do Boris** (missão **m4_coracao_de_sucata**)
   - A missão é ativada automaticamente quando você encontra o Boris
   - Você precisa comprar uma peça principal (motor, transmissão, etc.)
   - A missão é completada automaticamente quando você compra

2. **Voltar à garagem do Crank** (missão **m5_cirurgia_na_garagem**)
   - Após comprar do Boris, a cena `ch1_4_return_garage_upgrade` é iniciada
   - Você precisa instalar a peça comprada na garagem
   - A missão é completada automaticamente quando você instala um upgrade

3. **Fazer a primeira corrida** (missão **m6_batismo_de_pista**)
   - Após instalar o upgrade, a primeira corrida é desbloqueada
   - Você precisa completar a corrida no Circuito de Treino

## Implementações Realizadas

### 1. Completar missão m4 ao comprar do Boris
- **Arquivo**: `src/core/boris.py`
- **Função**: `processar_compra()`
- **Lógica**: Quando uma compra é bem-sucedida, verifica se a missão `m4_coracao_de_sucata` está ativa e a completa automaticamente.

### 2. Completar missão m5 ao instalar upgrade
- **Arquivo**: `src/core/menu.py`
- **Funções**: 
  - `tela_upgrades()` - quando upgrade é comprado sem confirmação
  - `tela_upgrades()` - quando upgrade é confirmado pelo Crank
- **Lógica**: Quando um upgrade é instalado, verifica se a missão `m5_cirurgia_na_garagem` está ativa e a completa automaticamente.

## Próximos Passos

Para melhorar ainda mais a organização:

1. Adicionar `completeOnSceneId` para missões que completam automaticamente (m4, m5)
2. Verificar se todas as missões têm objetivos claros
3. Garantir que o fluxo narrativo está alinhado com as missões



