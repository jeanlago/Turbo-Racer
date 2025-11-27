#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para traduzir todos os textos da narrativa para EN, ES e FR
Execute: python tools/traduzir_narrativa.py
"""

import json
import os
import sys

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from config import DIR_PROJETO

CAMINHO_NARRATIVA = os.path.join(DIR_PROJETO, "data", "narrative.json")
CAMINHO_LOCALES = os.path.join(DIR_PROJETO, "data", "locales")

# Traduções manuais (você pode expandir isso com uma API de tradução)
# Por enquanto, vou criar traduções básicas para demonstrar a estrutura

def traduzir_texto(texto_pt, idioma):
    """
    Traduz um texto do português para outro idioma
    Por enquanto retorna placeholder, mas pode ser integrado com API de tradução
    """
    # Esta é uma estrutura básica - você pode integrar com Google Translate API, DeepL, etc.
    # Por enquanto, vou criar traduções manuais para os primeiros textos como exemplo
    
    traducoes_exemplo = {
        "en": {
            "A cidade cheira a gasolina velha, fritura de esquina e sonho queimado. Seu carro faz parte disso.": 
                "The city smells of old gasoline, street food, and burned dreams. Your car is part of it.",
            "Você perdeu o trampo, perdeu a grana. Sobrou um carro semi-morto e um nome rabiscado num papel amassado: CRANK.":
                "You lost your job, lost your money. All that's left is a half-dead car and a name scribbled on a crumpled paper: CRANK.",
            "Dizem que se alguém consegue fazer motor morto rugir de novo, é ele. Dizem também que ele é um inferno de aturar.":
                "They say if anyone can make a dead engine roar again, it's him. They also say he's hell to deal with."
        },
        "es": {
            "A cidade cheira a gasolina velha, fritura de esquina e sonho queimado. Seu carro faz parte disso.":
                "La ciudad huele a gasolina vieja, comida callejera y sueños quemados. Tu coche es parte de eso.",
            "Você perdeu o trampo, perdeu a grana. Sobrou um carro semi-morto e um nome rabiscado num papel amassado: CRANK.":
                "Perdiste tu trabajo, perdiste tu dinero. Solo queda un coche medio muerto y un nombre garabateado en un papel arrugado: CRANK.",
            "Dizem que se alguém consegue fazer motor morto rugir de novo, é ele. Dizem também que ele é um inferno de aturar.":
                "Dicen que si alguien puede hacer rugir un motor muerto de nuevo, es él. También dicen que es un infierno de aguantar."
        },
        "fr": {
            "A cidade cheira a gasolina velha, fritura de esquina e sonho queimado. Seu carro faz parte disso.":
                "La ville sent l'essence vieille, la friture de rue et les rêves brûlés. Votre voiture en fait partie.",
            "Você perdeu o trampo, perdeu a grana. Sobrou um carro semi-morto e um nome rabiscado num papel amassado: CRANK.":
                "Vous avez perdu votre boulot, perdu votre argent. Il ne reste qu'une voiture à moitié morte et un nom griffonné sur un papier froissé : CRANK.",
            "Dizem que se alguém consegue fazer motor morto rugir de novo, é ele. Dizem também que ele é um inferno de aturar.":
                "On dit que si quelqu'un peut faire rugir un moteur mort à nouveau, c'est lui. On dit aussi qu'il est un enfer à supporter."
        }
    }
    
    if idioma in traducoes_exemplo and texto_pt in traducoes_exemplo[idioma]:
        return traducoes_exemplo[idioma][texto_pt]
    
    # Placeholder para textos não traduzidos ainda
    return f"[{idioma.upper()}] {texto_pt}"

def extrair_e_organizar_textos():
    """Extrai todos os textos da narrativa e organiza por capítulo/cena"""
    with open(CAMINHO_NARRATIVA, 'r', encoding='utf-8') as f:
        narrative_data = json.load(f)
    
    estrutura_traducao = {}
    
    for chapter in narrative_data.get("chapters", []):
        chapter_id = chapter.get("id")
        chapter_name = chapter.get("name", "")
        
        estrutura_traducao[chapter_id] = {
            "name": chapter_name,
            "scenes": {}
        }
        
        for scene in chapter.get("scenes", []):
            scene_id = scene.get("id")
            # Simplificar scene_id para chave
            scene_key = scene_id.replace(f"{chapter_id}_", "")
            
            estrutura_traducao[chapter_id]["scenes"][scene_key] = {
                "lines": {},
                "choices": []
            }
            
            # Extrair linhas por speaker
            for i, line in enumerate(scene.get("lines", [])):
                speaker = line.get("speaker", "").lower()
                text = line.get("text", "")
                
                if speaker not in estrutura_traducao[chapter_id]["scenes"][scene_key]["lines"]:
                    estrutura_traducao[chapter_id]["scenes"][scene_key]["lines"][speaker] = []
                
                estrutura_traducao[chapter_id]["scenes"][scene_key]["lines"][speaker].append({
                    "index": i,
                    "text": text
                })
            
            # Extrair escolhas
            for i, choice in enumerate(scene.get("choices", [])):
                estrutura_traducao[chapter_id]["scenes"][scene_key]["choices"].append({
                    "index": i,
                    "text": choice.get("text", "")
                })
    
    return estrutura_traducao

def gerar_traducao_completa(estrutura, idioma):
    """Gera estrutura completa de tradução para um idioma"""
    traducao = {}
    
    for chapter_id, chapter_data in estrutura.items():
        traducao[chapter_id] = {}
        
        for scene_key, scene_data in chapter_data["scenes"].items():
            traducao[chapter_id][scene_key] = {}
            
            # Traduzir linhas
            for speaker, lines in scene_data["lines"].items():
                traducao[chapter_id][scene_key][speaker] = {
                    "lines": []
                }
                for line_data in lines:
                    texto_pt = line_data["text"]
                    texto_traduzido = traduzir_texto(texto_pt, idioma)
                    traducao[chapter_id][scene_key][speaker]["lines"].append({
                        "index": line_data["index"],
                        "text": texto_traduzido
                    })
            
            # Traduzir escolhas
            if scene_data["choices"]:
                traducao[chapter_id][scene_key]["choices"] = []
                for choice_data in scene_data["choices"]:
                    texto_pt = choice_data["text"]
                    texto_traduzido = traduzir_texto(texto_pt, idioma)
                    traducao[chapter_id][scene_key]["choices"].append({
                        "index": choice_data["index"],
                        "text": texto_traduzido
                    })
    
    return traducao

def adicionar_traducao_ao_locale(idioma, traducao):
    """Adiciona tradução ao arquivo de locale"""
    caminho_locale = os.path.join(CAMINHO_LOCALES, f"{idioma}.json")
    
    # Carregar locale existente
    with open(caminho_locale, 'r', encoding='utf-8') as f:
        locale_data = json.load(f)
    
    # Adicionar seção narrative se não existir
    if "narrative" not in locale_data:
        locale_data["narrative"] = {}
    
    # Adicionar traduções dos capítulos
    if "chapters" not in locale_data["narrative"]:
        locale_data["narrative"]["chapters"] = {}
    
    locale_data["narrative"]["chapters"] = traducao
    
    # Salvar
    with open(caminho_locale, 'w', encoding='utf-8') as f:
        json.dump(locale_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Traduções adicionadas ao {idioma}.json")

if __name__ == "__main__":
    print("Extraindo textos da narrativa...")
    estrutura = extrair_e_organizar_textos()
    
    print("\nGerando traduções...")
    for idioma in ["en", "es", "fr"]:
        print(f"\nTraduzindo para {idioma}...")
        traducao = gerar_traducao_completa(estrutura, idioma)
        adicionar_traducao_ao_locale(idioma, traducao)
    
    print("\n✅ Processo concluído!")
    print("\n⚠️  NOTA: As traduções foram geradas com placeholders.")
    print("   Para traduções completas, você pode:")
    print("   1. Integrar com Google Translate API")
    print("   2. Usar DeepL API")
    print("   3. Traduzir manualmente os textos nos arquivos de locale")

