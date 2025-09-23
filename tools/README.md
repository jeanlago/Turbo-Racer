# 🛠️ Ferramentas de Debug e Teste

Esta pasta contém ferramentas auxilIAres para desenvolvimento e debug do Turbo Racer.

## 📁 Arquivos Disponíveis

### **test_debug.py**
**Propósito:** Teste básico de funcionalidades do jogo  
**Uso:** `python tools/test_debug.py`  
**Funcionalidades:**
- Testa carregamento de pista
- Verifica geração de rotas
- Testa conversão de coordenadas da câmera
- Valida inicIAlização do Pygame

### **debug_IA_travada.py**
**Propósito:** Debug visual de checkpoints e navegação da IA  
**Uso:** `python tools/debug_IA_travada.py`  
**Funcionalidades:**
- Analisa checkpoints existentes
- Verifica se checkpoints estão em áreas transitáveis
- Mostra visualização colorida dos problemas
- Identifica pontos problemáticos na navegação

### **test_audio.py**
**Propósito:** Teste do sistema de áudio  
**Uso:** `python tools/test_audio.py`  
**Funcionalidades:**
- Testa inicIAlização do mixer de áudio
- Verifica carregamento de músicas
- Testa reprodução de áudio
- Valida configurações de áudio

## 🚀 Como Usar

### **Executar Testes**
```bash
# Teste básico
python tools/test_debug.py

# Debug de IA
python tools/debug_IA_travada.py

# Teste de áudio
python tools/test_audio.py
```

### **Requisitos**
- Python 3.10+
- Pygame instalado
- Projeto configurado corretamente

## 📝 Notas

- Estes arquivos são **ferramentas de desenvolvimento**
- Não são necessários para executar o jogo principal
- Podem ser removidos em builds de produção
- Úteis para dIAgnosticar problemas durante desenvolvimento

---

**CrIAdo em:** Dezembro 2024  
**Propósito:** Ferramentas de desenvolvimento e debug
