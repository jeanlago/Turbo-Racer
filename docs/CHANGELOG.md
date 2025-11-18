# 📝 Changelog - Turbo Racer

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [3.2.2] - 2025-11-18

### Removido
- **Comentários Desnecessários** - Removidos comentários redundantes que apenas descreviam o código óbvio
- **Código Comentado** - Removido bloco grande de código comentado relacionado a fonte pixel art em `menu.py`
- **Funções Não Utilizadas** - Removidas funções que não eram chamadas em nenhum lugar:
  - `normalizar_texto()` - Função de normalização de texto não utilizada
  - `ponto_dentro_ret()` - Função wrapper desnecessária para `rect.collidepoint()`

### Modificado
- **Limpeza de Código** - Removidos comentários redundantes em:
  - `src/core/menu.py` - Comentários de layout, posicionamento e animação
  - `src/core/musica.py` - Comentários sobre configuração de áudio
  - `src/core/checkpoint_manager.py` - Comentários sobre cálculos de centralização
- **Código Mais Limpo** - Melhor legibilidade e manutenibilidade sem perder funcionalidade

### Corrigido
- **Manutenibilidade** - Código mais fácil de ler e manter, mantendo apenas comentários que explicam lógica complexa

---

## [3.2.1] - 2025-11-13

### Modificado
- **Nomenclatura de Classes e Variáveis** - Corrigidos nomes com "IA" no meio de palavras:
  - `GerencIAdorCorrida` → `GerenciadorCorrida`
  - `GerencIAdorMusica` → `GerenciadorMusica`
  - `gerencIAdor_musica` → `gerenciador_musica`
  - `inicIAda` → `iniciada`
  - `musica_aleatorIA` → `musica_aleatoria`
  - `tela_cheIA_sem_bordas` → `tela_cheia_sem_bordas`
  - E outras correções similares em todo o código

### Removido
- **Código Não Utilizado** - Removidas funções e classes não utilizadas:
  - Função `is_on_track()` (sempre retornava True)
  - Função `obter_waypoints_fallback()` (não utilizada)
  - Função `carregar_tempos_recorde_grip()` (não utilizada)
  - Classe `GerencIAdorDrift` (não utilizada)
- **Comentários Desnecessários** - Removidos comentários excessivos e docstrings redundantes

### Corrigido
- **Consistência de Nomenclatura** - Todo o código agora usa nomenclatura consistente em português
- **Manutenibilidade** - Código mais limpo e fácil de manter

---

## [3.1.0] - 2025-11-11

### Adicionado
- **Sistema GRIP Completo** - Migração completa para sistema de pistas GRIP com tiles dinâmicos
- **IA com Múltiplos Oponentes** - 3 IAs no modo 1 jogador, 2 IAs no modo 2 jogadores, com seleção aleatória de carros
- **Sistema de Spawn Points** - Editor permite definir múltiplos pontos de spawn por pista
- **Checkpoints Retangulares Rotacionáveis** - Checkpoints perpendiculares à pista com rotação manual (R, Q, E)
- **HUD Split-Screen Melhorado** - Velocímetros individuais e minimapa centralizado no modo 2 jogadores
- **Sistema de Posição e Voltas** - Exibição de posição (1st, 2nd) e voltas (1/2) para cada jogador no split-screen

### Modificado
- **Sistema de Pistas** - Removido sistema antigo baseado em imagens PNG, agora 100% baseado em tiles GRIP
- **Sistema de Colisão** - Simplificado para sistema GRIP (sem colisão hard, apenas redução de velocidade na grama)
- **Editor de Checkpoints** - Suporte completo para rotação de checkpoints e edição de spawn points
- **Sistema de IA** - Melhorado para encontrar checkpoint mais próximo quando travado, em vez de resetar
- **HUD 2 Jogadores** - Layout redesenhado com linha divisória preta, minimapa centralizado e posição/voltas individuais
- **Sistema de Spawn** - Seleção aleatória de spawn points para players e IAs

### Corrigido
- **Bots Resetando para Checkpoint 1** - IA agora encontra checkpoint mais próximo quando travado
- **Checkpoints Não Visíveis** - Melhorada visibilidade e detecção de checkpoints retangulares
- **Posicionamento HUD** - Corrigido alinhamento de posição/voltas no modo 2 jogadores
- **Minimapa Inconsistente** - Corrigido mapeamento de coordenadas do mundo para minimapa
- **Teleporte de Carros** - Prevenção de teleportes ao trocar de tiles

### Removido
- **Sistema Antigo de Pistas** - Removido `src/core/pista.py` e toda lógica relacionada
- **Sistema de Mapas PNG** - Removido suporte para mapas baseados em imagens PNG
- **Código Não Utilizado** - Limpeza completa de imports e funções não utilizadas
- **Classe PistaGrip** - Removida classe não utilizada de `pista_grip.py`
- **Fallbacks Antigos** - Removidos todos os fallbacks para sistema antigo de pistas

### Otimizado
- **Código Limpo** - Removido código não utilizado, melhor manutenibilidade
- **Imports** - Limpeza de imports não utilizados em todos os módulos
- **Performance** - Otimizações de renderização e detecção de colisão

---

## [3.0.0] - 2025-11-10

### Adicionado
- **Sistema de Pistas GRIP** - 9 pistas estilo GRIP com tiles dinâmicos e colisão pixel-based
- **Editor de Garagem** - Ferramenta visual para ajustar posição e tamanho dos carros na oficina
- **Sistema de Recordes e Troféus** - Persistência de melhores tempos e troféus por pista
- **Minimapa Completo** - Mostra posição do jogador, checkpoints e outros carros
- **Velocímetro e Nitro PNG** - Indicadores visuais usando imagens PNG com animação
- **Sistema de Tempos** - Tempo total, tempo por checkpoint e tempo por volta
- **Aviso "Contra Mão"** - Alerta visual quando jogador vai na direção errada
- **Menu de Recordes** - Visualização de recordes e troféus conquistados

### Modificado
- **Sistema de Checkpoints** - Agora retangulares e perpendiculares à pista
- **Sistema de Colisão** - Migrado para detecção pixel-based estilo GRIP
- **Sistema de Renderização** - Tiles dinâmicos baseados na posição do jogador
- **HUD** - Adicionado velocímetro, nitro, minimapa e tempos

---

## [2.5.0] - 2025-11-10

### Adicionado
- **Velocímetro Horizontal com PNGs** - Novo velocímetro horizontal usando imagens PNG (colorido e sem cor) com animação de preenchimento similar ao nitro
- **Sistema de Notificações Diferenciado** - Popup de notificações com ícones diferentes para música (disco de vinil rotativo) e outras notificações (ícone de notificação com efeito de piscar laranja)
- **Animação de Piscar para Notificações** - Efeito visual de piscar laranja para notificações não-musicais (borda e ícone)

### Modificado
- **Velocímetro** - Substituído velocímetro circular antigo por velocímetro horizontal moderno com número de velocidade e barra animada
- **Sistema de Recompensas** - Recompensas de corrida reduzidas (base: 500 → 150) para melhor balanceamento
- **Preços dos Carros** - Preços dos carros dobrados para tornar o progresso mais desafiador
- **Recompensas de Drift** - Reduzidas de pontuação/100 para pontuação/200
- **Layout da Oficina (Player 2)** - Corrigido espaçamento e posicionamento para corresponder ao layout do Player 1
- **Posicionamento do Nitro** - Nitro agora posicionado ao lado do número do velocímetro (à esquerda) em vez de embaixo
- **Posição do Velocímetro** - Movido para posição mais baixa na tela (Y: 600 → 650)

### Corrigido
- **Layout da Tela do Player 2** - Corrigido sobreposição de textos na seleção de carros do Player 2
- **Crash ao Pressionar ESC** - Corrigido crash ao pressionar ESC na tela de mudança de carro após terminar corrida
- **Posicionamento de Elementos HUD** - Ajustado espaçamento entre velocímetro e nitro

### Removido
- **Velocímetro Circular Antigo** - Removido velocímetro circular com ponteiro e toda lógica relacionada
- **Métodos Antigos do Velocímetro** - Removidos métodos `_calcular_ponta_ponteiro`, `_escala_atual_sprite`, `_calcular_centro_ponteiro`, `_rotozoom_com_pivo`

---

## [2.4.0] - 2025-11-10

### Adicionado
- **Sistema de Economia** - Sistema de dinheiro para desbloquear carros
- **Sistema de Troféus** - Troféus de ouro, prata, bronze e vazio baseados em posição ou pontuação
- **Tela de Fim de Jogo Redesenhada** - Popup sobre o jogo com informações de resultado e opções
- **Sistema de Recompensas** - Ganho de dinheiro por vencer corridas e fazer drift
- **Sistema de Progresso Persistente** - Salvamento automático de dinheiro e carros desbloqueados
- **Botões de Compra e Uso** - Interface para comprar e usar carros na oficina

### Modificado
- **Menu de Seleção de Carros** - Adicionado sistema de compra e desbloqueio de carros
- **Tela de Fim de Jogo** - Redesenhada para aparecer como popup sobre o jogo em execução
- **Sistema de Troféus** - Tamanho aumentado para melhor visibilidade (160x160px)
- **Layout da Oficina** - Melhorias visuais e espaçamento otimizado

### Corrigido
- **Hitbox dos Botões** - Correção de detecção de hover e clique na tela de fim de jogo
- **Espaçamento de Elementos** - Ajustes de posicionamento na tela de fim de jogo
- **Import Circular** - Resolvido problema de importação circular entre main.py e menu.py

---

## [2.3.0] - 2025-01-XX

### Adicionado
- **Menu de Pausa Completo** - Sistema de pausa com opções de continuar, reiniciar e voltar ao menu
- **Navegação por Teclado no Menu de Pausa** - Controles intuitivos com setas e ENTER/SPACE
- **Interface Visual de Pausa** - Overlay escuro com opções destacadas e animações suaves
- **Sistema de Otimização de Performance** - Melhorias significativas para atingir 100+ FPS
- **Câmera Dinâmica Aprimorada** - Sensação de aceleração com zoom adaptativo baseado na velocidade
- **Sistema de Dificuldade para Drift** - Tempo ajustável baseado na dificuldade (Fácil: 1:30, Médio: 1:00, Difícil: 0:30)
- **Seleção de Dificuldade Universal** - Disponível para 1 jogador em ambos os modos (Corrida e Drift)
- **Sistema de Pontuação de Drift Melhorado** - Pontuação automática baseada em derrapagem real (marcas de pneu)

### Modificado
- **Sistema de Performance** - Otimizações agressivas mantendo qualidade visual
- **Sistema de Skidmarks** - Marcas de pneu em todas as 4 rodas com frequência otimizada
- **Sistema de Partículas** - Controle inteligente de densidade para melhor performance
- **Sistema de Câmera** - Zoom inicial aumentado e transições mais responsivas
- **Sistema de HUD** - Renderização otimizada para evitar flickering
- **Sistema de Detecção de Colisão** - Amostras otimizadas para melhor performance

### Corrigido
- **Bugs de Hover no Menu** - Correção de inconsistência entre detecção e renderização de botões
- **Flickering do HUD** - HUD agora renderiza suavemente sem piscar
- **Performance de FPS** - Jogo agora roda consistentemente acima de 100 FPS
- **Marcas de Pneu** - Restauradas marcas em todas as 4 rodas durante drift
- **Tela de Vitória Duplicada** - Removida tela duplicada, mantida interface visual rica
- **Câmera Muito Distante** - Zoom inicial ajustado para melhor experiência de jogo

### Removido
- **Prints de Debug** - Removidas mensagens de console desnecessárias (fumaça, partículas)
- **Otimizações Excessivas** - Revertidas otimizações que comprometiam qualidade visual
- **Tela de Vitória Simplificada** - Removida versão simplificada em favor da interface rica

---

## [2.2.0] - 2025-09-XX

### Adicionado
- **Sistema de Skidmarks Avançado** - Marcas de pneu no drift com gerenciamento inteligente
- **Configurações de Performance** - FPS máximo configurável e otimizações de renderização

### Modificado
- **Sistema de Física de Carros** - Melhorias na física de drift e estabilidade
- **Sistema de Câmera** - Otimizações de performance e suavização de movimento
- **Sistema de HUD** - Velocímetro e ponteiro com configurações otimizadas
- **Sistema de Configuração** - Melhorias na gestão de configurações do jogo
- **Sistema de Mapas** - Detecção automática aprimorada e recarregamento dinâmico
- **Sistema de Partículas** - Curvas de fade suaves e animação de texturas

### Corrigido
- **Problemas de Assets** - Correção de imagens faltantes (Car2.png, Car4.png)
- **Sistema de Skidmarks** - Marcas permanentes e conexão adequada entre segmentos
- **Interface de Usuário** - Melhorias visuais nos ícones e elementos da interface
- **Sistema de Física** - Correção de bugs na detecção de drift e estabilidade
- **Performance de Renderização** - Otimizações para melhor FPS

### Removido
- **Arquivos de Debug** - Remoção de scripts de teste desnecessários (tools/debug_*.py)
- **Assets Duplicados** - Limpeza de algumas das imagens duplicadas e arquivos desnecessários
- **Documentação Redundante** - Consolidação de documentação duplicada
- **Arquivos de Mapa Debug** - Remoção de mapas de teste não utilizados

---

## [2.1.0] - 2025-09-XX

### Adicionado
- **Sistema de Navegação de Menu Melhorado** - Controles intuitivos com setas e A/D
- **Sistema de Mapas Escalável** - Detecção automática de mapas sem configuração manual
- **Recarregamento Dinâmico de Mapas** - Tecla R para recarregar mapas em tempo real
- **Interface de Modo de Jogo Otimizada** - Layout melhorado com espaçamentos ajustados
- **Instruções de Navegação** - Guias claros para controles do menu

### Modificado
- **Navegação do Menu Principal** - Ordem visual e lógica sincronizadas
- **Layout do Menu de Modo de Jogo** - Espaçamentos otimizados e elementos reposicionados
- **Sistema de Detecção de Mapas** - Escaneamento automático da pasta maps
- **Tratamento de Erros de Menu** - Correção de crash ao pressionar ESC

### Corrigido
- **Crash ao Pressionar ESC** - Problema de tipo de retorno corrigido
- **Sobreposição de Elementos** - Botões não sobrepõem mais opções de voltas
- **Navegação Inconsistente** - Ordem de navegação corrigida para corresponder ao layout visual

## [2.0.0] - 2025-09-XX

### Adicionado
- **Sistema de Modos de Jogo** - Suporte para 1 jogador, 2 jogadores e modo drift
- **Modo 2 Jogadores** - Split-screen com câmeras independentes e checkpoints separados
- **Modo Drift** - Sistema de pontuação com tempo limitado (2 minutos)
- **Sistema de Vitória** - Detecção automática de vencedor e parada de carros
- **Câmera Dinâmica** - Zoom e posição adaptativos baseados na velocidade
- **HUD Limpo** - Interface minimalista com elementos essenciais
- **Sistema de Pause** - Pausar/despausar com ESC
- **Navegação Melhorada** - ESC após vitória volta ao menu
- **Documentação Profissional** - Estrutura reorganizada e simplificada

### Modificado
- **Sistema de Checkpoints** - Detecção múltipla e checkpoints separados por jogador
- **Interface de Menus** - Fluxo de seleção de modo de jogo
- **Sistema de HUD** - Elementos removidos para interface mais limpa
- **Sistema de Controles** - Controles específicos para cada modo
- **Renderização** - Suporte para split-screen e câmeras independentes

### Corrigido
- **Bug de Checkpoints** - Checkpoints "fantasma" no modo 2 jogadores
- **Sistema de Vitória** - Parada automática de carros quando alguém vence
- **Navegação de Menus** - ESC após vitória agora volta ao menu
- **Câmera Tremulante** - Interpolação suave para evitar instabilidade
- **HUD Duplicado** - HUD correto para cada jogador no split-screen

### Removido
- **Elementos de HUD** - Minimapa, informações detalhadas, controles (disponíveis via debug)
- **Comandos de Debug** - Vários comandos F removidos para limpeza
- **Sistema Antigo** - Código legado de drift e corrida
- **Documentação Duplicada** - Documentos redundantes consolidados

---

## [1.0.0] - 2025-09-XX

### Adicionado
- **Sistema Base** - Estrutura inicial do jogo
- **Física de Carros** - Sistema de física realista com derrapagem
- **Sistema de IA** - Algoritmo Pure Pursuit para navegação
- **Editor de Checkpoints** - Interface visual para posicionamento
- **Sistema de Mapas** - Suporte para múltiplos mapas
- **Sistema de Áudio** - Música e efeitos sonoros
- **Interface de Menus** - Sistema de navegação completo
- **Sistema de HUD** - Interface de jogo com informações detalhadas

---

## Tipos de Mudanças

- **Adicionado** - Para novas funcionalidades
- **Modificado** - Para mudanças em funcionalidades existentes
- **Depreciado** - Para funcionalidades que serão removidas em versões futuras
- **Removido** - Para funcionalidades removidas nesta versão
- **Corrigido** - Para correções de bugs
- **Segurança** - Para correções de vulnerabilidades

---

## Versionamento

Este projeto usa [Versionamento Semântico](https://semver.org/lang/pt-BR/):

- **MAJOR** - Mudanças incompatíveis na API
- **MINOR** - Funcionalidades adicionadas de forma compatível
- **PATCH** - Correções de bugs compatíveis

---

## Como Contribuir

1. **Fork** o projeto
2. **Crie** uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. **Abra** um Pull Request

---

## Padrões de Commit

Use os seguintes prefixos para commits:

- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Documentação
- `style:` - Formatação, ponto e vírgula, etc.
- `refactor:` - Refatoração de código
- `test:` - Adição de testes
- `chore:` - Mudanças em build, dependências, etc.

### Exemplos:
```
feat: adicionar modo 2 jogadores
fix: corrigir bug de checkpoints no split-screen
docs: reorganizar estrutura da documentação
style: formatar código do menu principal
refactor: simplificar sistema de HUD
test: adicionar testes para física dos carros
chore: atualizar dependências do pygame
```

---

**Última atualização:** 18 de Novembro de 2025  
**Versão atual:** 3.2.2  
**Próxima versão:** 3.3.0 (planejada)