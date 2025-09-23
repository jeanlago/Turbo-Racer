# 📝 Changelog - Turbo Racer

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [2.1.0] - 2024-12-XX

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

## [2.0.0] - 2024-12-XX

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

## [1.0.0] - 2024-11-XX

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

**Última atualização:** Dezembro 2024  
**Versão atual:** 2.0.0  
**Próxima versão:** 2.1.0 (planejada)