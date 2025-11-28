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

from config import DIR_PROJETO, obter_caminho_sprite_dia_noite, definir_estado_dia_noite

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
    
    # Lista de sprites que suportam dia/noite (baseado no código)
    sprites_dia_noite = ["cidade", "oficina", "casa", "monte_akira", "autodromo_fora", "fabrica", "predio_rex", "iate_barao", "bunker"]
    
    # Verificar backgrounds
    print("=" * 60)
    print("BACKGROUNDS")
    print("=" * 60)
    backgrounds_faltantes = []
    backgrounds_existentes = []
    
    for bg_name in sorted(backgrounds_usados):
        filename = BG_MAPPING.get(bg_name, "cidade.png")
        nome_base = os.path.splitext(filename)[0]  # Remove extensão
        
        # Verificar se o sprite suporta dia/noite
        if nome_base in sprites_dia_noite:
            # Usar sistema dia/noite
            definir_estado_dia_noite('dia')
            caminho_dia = obter_caminho_sprite_dia_noite(nome_base, CAMINHO_BACKGROUNDS)
            definir_estado_dia_noite('noite')
            caminho_noite = obter_caminho_sprite_dia_noite(nome_base, CAMINHO_BACKGROUNDS)
            
            # Considerar existente se pelo menos uma versão existir
            dia_existe = os.path.exists(caminho_dia)
            noite_existe = os.path.exists(caminho_noite)
            
            if dia_existe or noite_existe:
                status_versao = ""
                if dia_existe and noite_existe:
                    status_versao = " (dia+noite)"
                elif dia_existe:
                    status_versao = " (apenas dia)"
                else:
                    status_versao = " (apenas noite)"
                backgrounds_existentes.append((bg_name, filename))
                print(f"[OK] {bg_name} -> {filename}{status_versao}")
            else:
                backgrounds_faltantes.append((bg_name, filename))
                print(f"[FALTANDO] {bg_name} -> {filename} (dia+noite)")
        else:
            # Verificação normal (sem dia/noite)
            bg_path = os.path.join(CAMINHO_BACKGROUNDS, filename)
            if os.path.exists(bg_path):
                backgrounds_existentes.append((bg_name, filename))
                print(f"[OK] {bg_name} -> {filename}")
            else:
                backgrounds_faltantes.append((bg_name, filename))
                print(f"[FALTANDO] {bg_name} -> {filename}")
    
    # Verificar sprites dia/noite
    print("\n" + "=" * 60)
    print("SPRITES DIA/NOITE")
    print("=" * 60)
    
    # Extrair nomes base dos backgrounds usados
    backgrounds_base = set()
    for bg_name in backgrounds_usados:
        filename = BG_MAPPING.get(bg_name, "cidade.png")
        nome_base = os.path.splitext(filename)[0]  # Remove extensão
        backgrounds_base.add(nome_base)
    
    # Verificar quais têm versões dia/noite
    sprites_completos = []
    sprites_parciais = []
    sprites_faltantes_dn = []
    
    for sprite_base in sorted(sprites_dia_noite):
        # Verificar versão dia
        definir_estado_dia_noite('dia')
        caminho_dia = obter_caminho_sprite_dia_noite(sprite_base, CAMINHO_BACKGROUNDS)
        dia_existe = os.path.exists(caminho_dia)
        
        # Verificar versão noite
        definir_estado_dia_noite('noite')
        caminho_noite = obter_caminho_sprite_dia_noite(sprite_base, CAMINHO_BACKGROUNDS)
        noite_existe = os.path.exists(caminho_noite)
        
        # Determinar status
        if dia_existe and noite_existe:
            status = "✅ COMPLETO"
            sprites_completos.append(sprite_base)
        elif dia_existe or noite_existe:
            status = "⚠️ PARCIAL"
            falta = "noite" if dia_existe else "dia"
            sprites_parciais.append((sprite_base, falta))
        else:
            status = "❌ FALTANDO"
            sprites_faltantes_dn.append(sprite_base)
        
        # Só mostrar se for usado na narrativa ou se estiver faltando
        if sprite_base in backgrounds_base or not (dia_existe and noite_existe):
            print(f"{status} {sprite_base.upper()}")
            print(f"  Dia:   {os.path.basename(caminho_dia):<30} {'✅' if dia_existe else '❌ FALTANDO'}")
            print(f"  Noite: {os.path.basename(caminho_noite):<30} {'✅' if noite_existe else '❌ FALTANDO'}")
    
    # Verificar arquivos alternativos que existem mas não são usados
    arquivos_ui = os.listdir(CAMINHO_BACKGROUNDS) if os.path.exists(CAMINHO_BACKGROUNDS) else []
    arquivos_relevantes = [
        'casa_tarde.png',
        'fabrica_tarde.png',
        'iate_barao_tarde.png',
        'escritorio_rex_noite.png',
        'sala_rex_noite.png',
        'esconderijo_pixel.png'
    ]
    
    arquivos_alternativos = []
    for arquivo in arquivos_relevantes:
        if arquivo in arquivos_ui:
            arquivos_alternativos.append(arquivo)
    
    if arquivos_alternativos:
        print(f"\n⚠️  Arquivos alternativos encontrados (não usados pelo sistema):")
        for arquivo in arquivos_alternativos:
            print(f"   - {arquivo}")
    
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
    
    print(f"\nSprites Dia/Noite:")
    print(f"  ✅ Completos: {len(sprites_completos)}/{len(sprites_dia_noite)}")
    if sprites_completos:
        print(f"     - {', '.join(sprites_completos)}")
    print(f"  ⚠️  Parciais: {len(sprites_parciais)}/{len(sprites_dia_noite)}")
    if sprites_parciais:
        for sprite, falta in sprites_parciais:
            print(f"     - {sprite} (falta {falta})")
    print(f"  ❌ Faltantes: {len(sprites_faltantes_dn)}/{len(sprites_dia_noite)}")
    if sprites_faltantes_dn:
        print(f"     - {', '.join(sprites_faltantes_dn)}")
    
    total_sprites = sum(len(s) for s in sprites_usados.values())
    total_existentes = sum(len(s) for s in sprites_existentes.values())
    total_faltantes = sum(len(s) for s in sprites_faltantes.values())
    
    print(f"\nSprites de Personagens:")
    print(f"  Existentes: {total_existentes}/{total_sprites}")
    print(f"  Faltantes: {total_faltantes}")
    
    # Lista detalhada de faltantes
    if backgrounds_faltantes:
        print(f"\n{'=' * 60}")
        print("BACKGROUNDS FALTANTES:")
        print("=" * 60)
        for bg_name, filename in backgrounds_faltantes:
            print(f"  - {bg_name} -> {filename}")
    
    if sprites_faltantes_dn:
        print(f"\n{'=' * 60}")
        print("SPRITES DIA/NOITE FALTANTES:")
        print("=" * 60)
        for sprite_base in sprites_faltantes_dn:
            definir_estado_dia_noite('dia')
            caminho_dia = obter_caminho_sprite_dia_noite(sprite_base, CAMINHO_BACKGROUNDS)
            definir_estado_dia_noite('noite')
            caminho_noite = obter_caminho_sprite_dia_noite(sprite_base, CAMINHO_BACKGROUNDS)
            print(f"\n{sprite_base.upper()}:")
            print(f"  - {os.path.basename(caminho_dia)}")
            print(f"  - {os.path.basename(caminho_noite)}")
        
        # Sugestões
        print(f"\n💡 Sugestões:")
        if os.path.exists(os.path.join(CAMINHO_BACKGROUNDS, 'casa_tarde.png')):
            print("   - Renomear casa_tarde.png → casa_dia.png (e criar casa_noite.png)")
        if os.path.exists(os.path.join(CAMINHO_BACKGROUNDS, 'fabrica_tarde.png')):
            print("   - Renomear fabrica_tarde.png → fabrica_dia.png (e criar fabrica_noite.png)")
        if os.path.exists(os.path.join(CAMINHO_BACKGROUNDS, 'iate_barao_tarde.png')):
            print("   - Renomear iate_barao_tarde.png → iate_barao_dia.png (e criar iate_barao_noite.png)")
    
    if sprites_faltantes:
        print(f"\n{'=' * 60}")
        print("SPRITES DE PERSONAGENS FALTANTES:")
        print("=" * 60)
        for character_id, sprite_names in sorted(sprites_faltantes.items()):
            print(f"\n{character_id.upper()}:")
            for sprite_name in sprite_names:
                print(f"  - {sprite_name}.png")
                sprite_path = os.path.join(CAMINHO_SPRITES_CHARACTERS, character_id, f"{sprite_name}.png")
                print(f"    Caminho esperado: {sprite_path}")

if __name__ == "__main__":
    main()

