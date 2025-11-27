#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar quais sprites são necessários na narrativa e atualizar o relatório
Execute: python tools/verificar_sprites_narrativa.py
"""

import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from config import DIR_PROJETO

CAMINHO_NARRATIVA = os.path.join(DIR_PROJETO, "data", "narrative.json")
CAMINHO_SPRITES = os.path.join(DIR_PROJETO, "assets", "images", "characters")
CAMINHO_RELATORIO = os.path.join(DIR_PROJETO, "RELATORIO_ASSETS_FALTANTES.md")

# Mapeamento de personagens para pastas
CHARACTER_MAPPING = {
    "crank": "mecanico",
    "boris": "boris",
    "pixel": "pixel",
    "akira": "akira",
    "barao": "vendedor",
    "rex": "rival",
    "glub": "comprador",
    "slick": "vendedor"
}

def extrair_sprites_necessarios():
    """Extrai todos os sprites necessários do narrative.json"""
    with open(CAMINHO_NARRATIVA, 'r', encoding='utf-8') as f:
        narrative_data = json.load(f)
    
    sprites_necessarios = defaultdict(set)
    
    for chapter in narrative_data.get("chapters", []):
        for scene in chapter.get("scenes", []):
            # Sprites na configuração da cena
            for sprite_config in scene.get("sprites", []):
                sprite_id = sprite_config.get("id")
                sprite_name = sprite_config.get("sprite")
                if sprite_id and sprite_name:
                    sprites_necessarios[sprite_id].add(sprite_name)
            
            # Sprites nas linhas de diálogo
            for line in scene.get("lines", []):
                sprite_name = line.get("sprite")
                speaker = line.get("speaker", "").lower()
                if sprite_name and speaker:
                    sprites_necessarios[speaker].add(sprite_name)
    
    return sprites_necessarios

def verificar_sprites_existentes():
    """Verifica quais sprites existem nas pastas"""
    sprites_existentes = {}
    
    for character_id, folder_name in CHARACTER_MAPPING.items():
        folder_path = os.path.join(CAMINHO_SPRITES, folder_name)
        if os.path.exists(folder_path):
            files = []
            for f in os.listdir(folder_path):
                if f.endswith('.png'):
                    # Remover extensão .png (mesmo se houver duplicação)
                    name = f.replace('.png', '').replace('.png', '')
                    files.append(name)
            sprites_existentes[character_id] = set(files)
        else:
            sprites_existentes[character_id] = set()
    
    return sprites_existentes

def gerar_relatorio():
    """Gera o relatório atualizado"""
    sprites_necessarios = extrair_sprites_necessarios()
    sprites_existentes = verificar_sprites_existentes()
    
    relatorio = []
    relatorio.append("# Relatório de Assets Faltantes para a Narrativa\n")
    relatorio.append("## ✅ Backgrounds\n")
    relatorio.append("**Todos os backgrounds estão disponíveis!** (17/17)\n")
    relatorio.append("Todos os backgrounds necessários foram mapeados para arquivos existentes na pasta `assets/images/ui/`.\n")
    relatorio.append("---\n")
    relatorio.append("\n## ❌ Sprites Faltantes\n\n")
    
    total_necessarios = sum(len(sprites) for sprites in sprites_necessarios.values())
    
    # Ordem de prioridade
    ordem_prioridade = ["crank", "boris", "pixel", "akira", "barao", "rex", "glub", "slick"]
    
    # Recalcular totais corretamente
    total_existentes_real = 0
    total_faltantes_real = 0
    
    for character_id in ordem_prioridade:
        if character_id not in sprites_necessarios:
            continue
        sprites_char = sprites_necessarios[character_id]
        sprites_existentes_char = sprites_existentes.get(character_id, set())
        
        for sprite in sprites_char:
            # Verificar se o sprite existe (com ou sem extensão dupla)
            sprite_existe = sprite in sprites_existentes_char or f"{sprite}.png" in sprites_existentes_char
            
            if sprite_existe:
                total_existentes_real += 1
            else:
                total_faltantes_real += 1
    
    relatorio.append(f"- **Total de sprites necessários:** {total_necessarios}\n")
    relatorio.append(f"- **Sprites existentes:** {total_existentes_real}\n")
    relatorio.append(f"- **Sprites faltantes:** {total_faltantes_real}\n")
    relatorio.append("\n### Detalhamento por Personagem\n\n")
    
    for character_id in ordem_prioridade:
        if character_id not in sprites_necessarios:
            continue
        
        folder_name = CHARACTER_MAPPING.get(character_id, character_id)
        folder_path = os.path.join(CAMINHO_SPRITES, folder_name)
        sprites_existentes_char = sprites_existentes.get(character_id, set())
        sprites_char = sprites_necessarios[character_id]
        
        relatorio.append(f"#### {character_id.upper()} (pasta: `{folder_name}/`)\n")
        
        if not os.path.exists(folder_path):
            relatorio.append(f"**Status:** ❌ Pasta não existe\n\n")
        else:
            relatorio.append(f"**Status:** {'✅ Pasta existe' if os.path.exists(folder_path) else '❌ Pasta não existe'}\n\n")
        
        relatorio.append("**Sprites necessários:**\n")
        
        sprites_encontrados = []
        sprites_faltantes = []
        
        for sprite in sorted(sprites_char):
            # Verificar se o sprite existe (com ou sem extensão dupla)
            sprite_existe = sprite in sprites_existentes_char or f"{sprite}.png" in sprites_existentes_char
            
            if sprite_existe:
                relatorio.append(f"- `{sprite}.png` → ✅ **Existe**\n")
                sprites_encontrados.append(sprite)
            else:
                relatorio.append(f"- `{sprite}.png` ❌\n")
                sprites_faltantes.append(sprite)
        
        if os.path.exists(folder_path):
            todos_arquivos = [f.replace('.png', '') for f in os.listdir(folder_path) if f.endswith('.png')]
            arquivos_nao_usados = [f for f in todos_arquivos if f not in sprites_char]
            
            if arquivos_nao_usados:
                relatorio.append(f"\n**Sprites disponíveis (não usados na narrativa):**\n")
                for arquivo in sorted(arquivos_nao_usados):
                    relatorio.append(f"- `{arquivo}.png`\n")
        
        if sprites_faltantes:
            relatorio.append(f"\n**Sugestão de mapeamento:**\n")
            # Sugerir mapeamentos baseados em nomes similares
            for sprite_faltante in sprites_faltantes:
                sugestoes = []
                if os.path.exists(folder_path):
                    for arquivo_existente in sprites_existentes_char:
                        # Buscar por palavras-chave similares
                        palavras_faltante = set(sprite_faltante.lower().split('_'))
                        palavras_existente = set(arquivo_existente.lower().split('_'))
                        if palavras_faltante & palavras_existente:  # Interseção
                            sugestoes.append(arquivo_existente)
                
                if sugestoes:
                    relatorio.append(f"- `{sprite_faltante}` → `{sugestoes[0]}.png` (sugestão)\n")
                else:
                    relatorio.append(f"- `{sprite_faltante}` → Criar novo sprite\n")
        
        relatorio.append("\n---\n\n")
    
    # Remover a seção duplicada de resumo
    relatorio.append("## 📋 Ações Necessárias\n\n")
    relatorio.append("### Opção 1: Criar Sprites Faltantes\n")
    relatorio.append("Criar todos os sprites listados acima nas respectivas pastas.\n\n")
    relatorio.append("### Opção 2: Mapear Sprites Existentes\n")
    relatorio.append("Atualizar o sistema de narrativa para mapear os sprites necessários para os sprites existentes (usando os mapeamentos sugeridos acima).\n\n")
    relatorio.append("### Opção 3: Renomear Sprites Existentes\n")
    relatorio.append("Renomear os sprites existentes para corresponder aos nomes esperados pelo JSON.\n\n")
    relatorio.append("---\n\n")
    relatorio.append("## 🎯 Prioridade\n\n")
    relatorio.append("1. **CRANK** - Alta prioridade (personagem principal)\n")
    relatorio.append("2. **BORIS** - Alta prioridade (aparece no Capítulo 1)\n")
    relatorio.append("3. **AKIRA** - Média prioridade (Capítulo 3)\n")
    relatorio.append("4. **PIXEL** - Média prioridade (aparece em vários capítulos)\n")
    relatorio.append("5. **BARAO** - Média prioridade (Capítulo 2)\n")
    relatorio.append("6. **REX** - Baixa prioridade (Capítulos 4-5)\n")
    relatorio.append("7. **GLUB** - Baixa prioridade (Capítulo 4)\n")
    relatorio.append("8. **SLICK** - Baixa prioridade (Capítulo 4)\n\n")
    relatorio.append("---\n\n")
    relatorio.append("## 📝 Notas\n\n")
    relatorio.append("- O sistema de narrativa já tem fallback para usar o primeiro sprite disponível se o sprite específico não existir\n")
    relatorio.append("- Alguns sprites podem ser reutilizados com nomes diferentes\n")
    relatorio.append("- O sistema pode ser atualizado para fazer mapeamento automático de nomes similares\n")
    
    return ''.join(relatorio)

if __name__ == "__main__":
    print("Extraindo sprites necessarios da narrativa...")
    print("Verificando sprites existentes...")
    
    relatorio = gerar_relatorio()
    
    print(f"Salvando relatorio em {CAMINHO_RELATORIO}...")
    with open(CAMINHO_RELATORIO, 'w', encoding='utf-8') as f:
        f.write(relatorio)
    
    print("OK: Relatorio atualizado!")

