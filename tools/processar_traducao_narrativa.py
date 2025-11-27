#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para processar e adicionar traduções da narrativa aos arquivos de locale
Execute: python tools/processar_traducao_narrativa.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from config import DIR_PROJETO

CAMINHO_NARRATIVA = os.path.join(DIR_PROJETO, "data", "narrative.json")
CAMINHO_LOCALES = os.path.join(DIR_PROJETO, "data", "locales")

# Traduções manuais dos textos principais
# Por enquanto, vou criar uma estrutura básica que pode ser expandida

TRADUCOES_MANUAIS = {
    "ch1_0_prologue": {
        "narrator": {
            "lines": [
                {
                    "pt": "A cidade cheira a gasolina velha, fritura de esquina e sonho queimado. Seu carro faz parte disso.",
                    "en": "The city smells of old gasoline, street food, and burned dreams. Your car is part of it.",
                    "es": "La ciudad huele a gasolina vieja, comida callejera y sueños quemados. Tu coche es parte de eso.",
                    "fr": "La ville sent l'essence vieille, la friture de rue et les rêves brûlés. Votre voiture en fait partie."
                },
                {
                    "pt": "Você perdeu o trampo, perdeu a grana. Sobrou um carro semi-morto e um nome rabiscado num papel amassado: CRANK.",
                    "en": "You lost your job, lost your money. All that's left is a half-dead car and a name scribbled on a crumpled paper: CRANK.",
                    "es": "Perdiste tu trabajo, perdiste tu dinero. Solo queda un coche medio muerto y un nombre garabateado en un papel arrugado: CRANK.",
                    "fr": "Vous avez perdu votre boulot, perdu votre argent. Il ne reste qu'une voiture à moitié morte et un nom griffonné sur un papier froissé : CRANK."
                },
                {
                    "pt": "Dizem que se alguém consegue fazer motor morto rugir de novo, é ele. Dizem também que ele é um inferno de aturar.",
                    "en": "They say if anyone can make a dead engine roar again, it's him. They also say he's hell to deal with.",
                    "es": "Dicen que si alguien puede hacer rugir un motor muerto de nuevo, es él. También dicen que es un infierno de aguantar.",
                    "fr": "On dit que si quelqu'un peut faire rugir un moteur mort à nouveau, c'est lui. On dit aussi qu'il est un enfer à supporter."
                }
            ]
        }
    }
}

def processar_e_adicionar_traducao():
    """Processa a narrativa e adiciona traduções aos arquivos de locale"""
    
    with open(CAMINHO_NARRATIVA, 'r', encoding='utf-8') as f:
        narrative_data = json.load(f)
    
    # Estrutura de traduções por idioma
    traducoes_por_idioma = {
        "en": {},
        "es": {},
        "fr": {}
    }
    
    # Processar cada capítulo
    for chapter in narrative_data.get("chapters", []):
        chapter_id = chapter.get("id")
        
        # Traduzir nome do capítulo
        nomes_capitulos = {
            "ch1": {"en": "Rust and First Race", "es": "Óxido y Primera Carrera", "fr": "Rouille et Première Course"},
            "ch2": {"en": "Contract with the Baron", "es": "Contrato con el Barón", "fr": "Contrat avec le Baron"},
            "ch3": {"en": "Mountain Flow", "es": "Flujo de la Montaña", "fr": "Flux de la Montagne"},
            "ch4": {"en": "Eyes in the Towers", "es": "Ojos en las Torres", "fr": "Yeux dans les Tours"},
            "ch5": {"en": "King's Game", "es": "Juego del Rey", "fr": "Jeu du Roi"}
        }
        
        for idioma in ["en", "es", "fr"]:
            if chapter_id not in traducoes_por_idioma[idioma]:
                traducoes_por_idioma[idioma][chapter_id] = {
                    "name": nomes_capitulos.get(chapter_id, {}).get(idioma, chapter.get("name", "")),
                    "scenes": {}
                }
        
        # Processar cada cena
        for scene in chapter.get("scenes", []):
            scene_id = scene.get("id")
            scene_key = scene_id.replace(f"{chapter_id}_", "")
            
            for idioma in ["en", "es", "fr"]:
                if scene_key not in traducoes_por_idioma[idioma][chapter_id]["scenes"]:
                    traducoes_por_idioma[idioma][chapter_id]["scenes"][scene_key] = {
                        "lines": {},
                        "choices": []
                    }
            
            # Processar linhas
            for line in scene.get("lines", []):
                speaker = line.get("speaker", "").lower()
                text_pt = line.get("text", "")
                
                # Por enquanto, criar placeholder
                # Em produção, você pode usar uma API de tradução ou traduções manuais
                for idioma in ["en", "es", "fr"]:
                    if speaker not in traducoes_por_idioma[idioma][chapter_id]["scenes"][scene_key]["lines"]:
                        traducoes_por_idioma[idioma][chapter_id]["scenes"][scene_key]["lines"][speaker] = []
                    
                    # Placeholder - será substituído por traduções reais
                    traducoes_por_idioma[idioma][chapter_id]["scenes"][scene_key]["lines"][speaker].append({
                        "text": f"[{idioma.upper()}] {text_pt}"
                    })
            
            # Processar escolhas
            for choice in scene.get("choices", []):
                text_pt = choice.get("text", "")
                for idioma in ["en", "es", "fr"]:
                    traducoes_por_idioma[idioma][chapter_id]["scenes"][scene_key]["choices"].append({
                        "text": f"[{idioma.upper()}] {text_pt}"
                    })
    
    # Adicionar aos arquivos de locale
    for idioma in ["en", "es", "fr"]:
        caminho_locale = os.path.join(CAMINHO_LOCALES, f"{idioma}.json")
        
        with open(caminho_locale, 'r', encoding='utf-8') as f:
            locale_data = json.load(f)
        
        if "narrative" not in locale_data:
            locale_data["narrative"] = {}
        
        locale_data["narrative"]["chapters"] = traducoes_por_idioma[idioma]
        
        with open(caminho_locale, 'w', encoding='utf-8') as f:
            json.dump(locale_data, f, ensure_ascii=False, indent=2)
        
        print(f"OK: Traducoes adicionadas ao {idioma}.json")
    
    print("\nNOTA: As traducoes foram geradas com placeholders.")
    print("   Para traduções completas, você precisa:")
    print("   1. Integrar com Google Translate API ou DeepL")
    print("   2. Traduzir manualmente os textos")
    print("   3. Usar uma ferramenta de tradução de JSON")

if __name__ == "__main__":
    print("Processando narrativa e adicionando traduções...")
    processar_e_adicionar_traducao()
    print("\nOK: Processo concluido!")

