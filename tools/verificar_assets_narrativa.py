#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar quais sprites e backgrounds estão faltando para a narrativa
Execute: python tools/verificar_assets_narrativa.py
"""

import json
import os
import sys
from collections import defaultdict

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from config import DIR_PROJETO

CAMINHO_NARRATIVA = os.path.join(DIR_PROJETO, "data", "narrative.json")
CAMINHO_BACKGROUNDS = os.path.join(DIR_PROJETO, "assets", "images", "ui")
CAMINHO_SPRITES_CHARACTERS = os.path.join(DIR_PROJETO, "assets", "images", "characters")

# Mapeamento de backgrounds
BG_MAPPING = {
    "bg_rua_chuva": "cidade.png",
    "bg_garagem": "oficina.png",
    "bg_garagem_noite": "oficina.png",  # TODO: criar versão noturna
    "bg_fosso_ferrugem": "fabrica.png",
    "bg_mapa_cidade": "cidade.png",
    "bg_santuario_montanha": "monte_akira.png",
    "bg_cobertura_corporativa": "predio_rex.png",
    "bg_beco_neon": "cidade.png",
    "bg_beco_sucata": "fabrica.png",
    "bg_apartamento_jogador": "casa.png",
    "bg_grid_circuito_urbano": "autodromo_fora.png",
    "bg_pit_circuito": "oficina.png",
    "bg_circuito_industrial": "fabrica.png",
    "bg_circuito_hibrido": "cidade.png",
    "bg_camarim_circuito": "predio_rex.png",
    "bg_podio": "autodromo_fora.png",
    "bg_torre_alta": "predio_rex.png"
}

def main():
    """Verifica assets faltantes"""
    # Carregar narrativa
    try:
        with open(CAMINHO_NARRATIVA, 'r', encoding='utf-8') as f:
            narrative_data = json.load(f)
    except Exception as e:
        print(f"Erro ao carregar narrativa: {e}")
        return
    
    # Coletar todos os sprites e backgrounds usados
    backgrounds_usados = set()
    sprites_usados = defaultdict(set)  # {character_id: {sprite_names}}
    
    for chapter in narrative_data.get("chapters", []):
        for scene in chapter.get("scenes", []):
            # Backgrounds
            bg = scene.get("bg")
            if bg:
                backgrounds_usados.add(bg)
            
            # Sprites da cena
            for sprite_config in scene.get("sprites", []):
                sprite_id = sprite_config.get("id")
                sprite_name = sprite_config.get("sprite")
                if sprite_id and sprite_name:
                    sprites_usados[sprite_id].add(sprite_name)
            
            # Sprites nas linhas de diálogo
            for line in scene.get("lines", []):
                sprite_name = line.get("sprite")
                speaker = line.get("speaker", "").upper()
                if sprite_name and speaker:
                    # Converter speaker para character_id (lowercase)
                    character_id = speaker.lower()
                    sprites_usados[character_id].add(sprite_name)
    
    # Verificar backgrounds
    print("=" * 60)
    print("BACKGROUNDS")
    print("=" * 60)
    backgrounds_faltantes = []
    backgrounds_existentes = []
    
    for bg_name in sorted(backgrounds_usados):
        filename = BG_MAPPING.get(bg_name, "cidade.png")
        bg_path = os.path.join(CAMINHO_BACKGROUNDS, filename)
        if os.path.exists(bg_path):
            backgrounds_existentes.append((bg_name, filename))
            print(f"[OK] {bg_name} -> {filename}")
        else:
            backgrounds_faltantes.append((bg_name, filename))
            print(f"[FALTANDO] {bg_name} -> {filename}")
    
    # Verificar sprites
    print("\n" + "=" * 60)
    print("SPRITES DE PERSONAGENS")
    print("=" * 60)
    sprites_faltantes = defaultdict(list)
    sprites_existentes = defaultdict(list)
    
    for character_id, sprite_names in sorted(sprites_usados.items()):
        print(f"\n{character_id.upper()}:")
        character_dir = os.path.join(CAMINHO_SPRITES_CHARACTERS, character_id)
        
        if not os.path.exists(character_dir):
            print(f"  [ERRO] Pasta não existe: {character_dir}")
            for sprite_name in sprite_names:
                sprites_faltantes[character_id].append(sprite_name)
                print(f"    [FALTANDO] {sprite_name}.png (pasta não existe)")
            continue
        
        # Listar arquivos disponíveis
        arquivos_disponiveis = [f.replace('.png', '') for f in os.listdir(character_dir) if f.endswith('.png')]
        
        for sprite_name in sorted(sprite_names):
            sprite_file = f"{sprite_name}.png"
            sprite_path = os.path.join(character_dir, sprite_file)
            
            if os.path.exists(sprite_path):
                sprites_existentes[character_id].append(sprite_name)
                print(f"  [OK] {sprite_name}.png")
            else:
                sprites_faltantes[character_id].append(sprite_name)
                print(f"  [FALTANDO] {sprite_name}.png")
                # Sugerir sprites similares
                similares = [a for a in arquivos_disponiveis if sprite_name.lower() in a.lower() or a.lower() in sprite_name.lower()]
                if similares:
                    print(f"    -> Sugestoes: {', '.join(similares)}")
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)
    print(f"\nBackgrounds:")
    print(f"  Existentes: {len(backgrounds_existentes)}/{len(backgrounds_usados)}")
    print(f"  Faltantes: {len(backgrounds_faltantes)}")
    
    total_sprites = sum(len(s) for s in sprites_usados.values())
    total_existentes = sum(len(s) for s in sprites_existentes.values())
    total_faltantes = sum(len(s) for s in sprites_faltantes.values())
    
    print(f"\nSprites:")
    print(f"  Existentes: {total_existentes}/{total_sprites}")
    print(f"  Faltantes: {total_faltantes}")
    
    # Lista detalhada de faltantes
    if backgrounds_faltantes:
        print(f"\n{'=' * 60}")
        print("BACKGROUNDS FALTANTES:")
        print("=" * 60)
        for bg_name, filename in backgrounds_faltantes:
            print(f"  - {bg_name} -> {filename}")
    
    if sprites_faltantes:
        print(f"\n{'=' * 60}")
        print("SPRITES FALTANTES:")
        print("=" * 60)
        for character_id, sprite_names in sorted(sprites_faltantes.items()):
            print(f"\n{character_id.upper()}:")
            for sprite_name in sprite_names:
                print(f"  - {sprite_name}.png")
                sprite_path = os.path.join(CAMINHO_SPRITES_CHARACTERS, character_id, f"{sprite_name}.png")
                print(f"    Caminho esperado: {sprite_path}")

if __name__ == "__main__":
    main()

