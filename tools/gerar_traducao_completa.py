#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gerar traduções completas da narrativa
Este script cria um arquivo JSON com todas as traduções organizadas
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from config import DIR_PROJETO

CAMINHO_NARRATIVA = os.path.join(DIR_PROJETO, "data", "narrative.json")
CAMINHO_TRADUCOES = os.path.join(DIR_PROJETO, "data", "traducoes_narrativa.json")

# Dicionário de traduções (você pode expandir isso)
# Por enquanto, vou criar uma estrutura básica que pode ser preenchida

def processar_narrativa():
    """Processa a narrativa e gera estrutura de tradução"""
    with open(CAMINHO_NARRATIVA, 'r', encoding='utf-8') as f:
        narrative_data = json.load(f)
    
    traducoes = {
        "en": {},
        "es": {},
        "fr": {}
    }
    
    for chapter in narrative_data.get("chapters", []):
        chapter_id = chapter.get("id")
        chapter_name = chapter.get("name", "")
        
        # Traduzir nome do capítulo
        nomes_capitulos = {
            "ch1": {
                "en": "Rust and First Race",
                "es": "Óxido y Primera Carrera",
                "fr": "Rouille et Première Course"
            },
            "ch2": {
                "en": "Contract with the Baron",
                "es": "Contrato con el Barón",
                "fr": "Contrat avec le Baron"
            },
            "ch3": {
                "en": "Mountain Flow",
                "es": "Flujo de la Montaña",
                "fr": "Flux de la Montagne"
            },
            "ch4": {
                "en": "Eyes in the Towers",
                "es": "Ojos en las Torres",
                "fr": "Yeux dans les Tours"
            },
            "ch5": {
                "en": "King's Game",
                "es": "Juego del Rey",
                "fr": "Jeu du Roi"
            }
        }
        
        for idioma in ["en", "es", "fr"]:
            if chapter_id not in traducoes[idioma]:
                traducoes[idioma][chapter_id] = {
                    "name": nomes_capitulos.get(chapter_id, {}).get(idioma, chapter_name),
                    "scenes": {}
                }
        
        for scene in chapter.get("scenes", []):
            scene_id = scene.get("id")
            scene_key = scene_id.replace(f"{chapter_id}_", "")
            
            for idioma in ["en", "es", "fr"]:
                if scene_key not in traducoes[idioma][chapter_id]["scenes"]:
                    traducoes[idioma][chapter_id]["scenes"][scene_key] = {
                        "lines": {},
                        "choices": []
                    }
            
            # Processar linhas
            for line in scene.get("lines", []):
                speaker = line.get("speaker", "").lower()
                text_pt = line.get("text", "")
                
                # Por enquanto, criar placeholder
                # Você pode integrar com API de tradução aqui
                for idioma in ["en", "es", "fr"]:
                    if speaker not in traducoes[idioma][chapter_id]["scenes"][scene_key]["lines"]:
                        traducoes[idioma][chapter_id]["scenes"][scene_key]["lines"][speaker] = []
                    
                    # Placeholder - será substituído por traduções reais
                    traducoes[idioma][chapter_id]["scenes"][scene_key]["lines"][speaker].append({
                        "text": f"[{idioma.upper()}] {text_pt}"
                    })
            
            # Processar escolhas
            for choice in scene.get("choices", []):
                text_pt = choice.get("text", "")
                for idioma in ["en", "es", "fr"]:
                    traducoes[idioma][chapter_id]["scenes"][scene_key]["choices"].append({
                        "text": f"[{idioma.upper()}] {text_pt}"
                    })
    
    return traducoes

if __name__ == "__main__":
    print("Processando narrativa...")
    traducoes = processar_narrativa()
    
    print(f"Salvando em {CAMINHO_TRADUCOES}...")
    with open(CAMINHO_TRADUCOES, 'w', encoding='utf-8') as f:
        json.dump(traducoes, f, ensure_ascii=False, indent=2)
    
    print("✅ Estrutura de tradução criada!")
    print("\n⚠️  NOTA: As traduções estão como placeholders.")
    print("   Você precisa preencher as traduções reais no arquivo gerado.")

