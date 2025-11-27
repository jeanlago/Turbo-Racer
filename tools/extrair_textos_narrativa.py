#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extrair todos os textos da narrativa e gerar estrutura de tradução
Execute: python tools/extrair_textos_narrativa.py
"""

import json
import os
import sys
from collections import defaultdict

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from config import DIR_PROJETO

CAMINHO_NARRATIVA = os.path.join(DIR_PROJETO, "data", "narrative.json")

def extrair_textos():
    """Extrai todos os textos da narrativa"""
    with open(CAMINHO_NARRATIVA, 'r', encoding='utf-8') as f:
        narrative_data = json.load(f)
    
    textos = {}
    
    for chapter in narrative_data.get("chapters", []):
        chapter_id = chapter.get("id")
        chapter_name = chapter.get("name", "")
        
        textos[chapter_id] = {
            "name": chapter_name,
            "scenes": {}
        }
        
        for scene in chapter.get("scenes", []):
            scene_id = scene.get("id")
            textos[chapter_id]["scenes"][scene_id] = {
                "lines": [],
                "choices": []
            }
            
            # Extrair linhas
            for i, line in enumerate(scene.get("lines", [])):
                textos[chapter_id]["scenes"][scene_id]["lines"].append({
                    "index": i,
                    "speaker": line.get("speaker", ""),
                    "text": line.get("text", "")
                })
            
            # Extrair escolhas
            for i, choice in enumerate(scene.get("choices", [])):
                textos[chapter_id]["scenes"][scene_id]["choices"].append({
                    "index": i,
                    "text": choice.get("text", "")
                })
    
    return textos

def gerar_chaves_traducao(textos):
    """Gera estrutura de chaves de tradução"""
    estrutura = {}
    
    for chapter_id, chapter_data in textos.items():
        estrutura[chapter_id] = {}
        
        for scene_id, scene_data in chapter_data["scenes"].items():
            # Simplificar scene_id para chave
            scene_key = scene_id.replace(f"{chapter_id}_", "")
            
            if scene_key not in estrutura[chapter_id]:
                estrutura[chapter_id][scene_key] = {}
            
            # Adicionar linhas
            for line_data in scene_data["lines"]:
                speaker_lower = line_data["speaker"].lower()
                line_index = line_data["index"]
                
                if speaker_lower not in estrutura[chapter_id][scene_key]:
                    estrutura[chapter_id][scene_key][speaker_lower] = {}
                
                if "lines" not in estrutura[chapter_id][scene_key][speaker_lower]:
                    estrutura[chapter_id][scene_key][speaker_lower]["lines"] = []
                
                estrutura[chapter_id][scene_key][speaker_lower]["lines"].append({
                    "index": line_index,
                    "text": line_data["text"]
                })
            
            # Adicionar escolhas
            if scene_data["choices"]:
                if "choices" not in estrutura[chapter_id][scene_key]:
                    estrutura[chapter_id][scene_key]["choices"] = []
                
                for choice_data in scene_data["choices"]:
                    estrutura[chapter_id][scene_key]["choices"].append({
                        "index": choice_data["index"],
                        "text": choice_data["text"]
                    })
    
    return estrutura

if __name__ == "__main__":
    textos = extrair_textos()
    estrutura = gerar_chaves_traducao(textos)
    
    print("Estrutura de textos extraída:")
    print(json.dumps(estrutura, ensure_ascii=False, indent=2))

