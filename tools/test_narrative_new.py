#!/usr/bin/env python3
"""
Script de teste para o novo sistema narrativo com gatilhos dinâmicos
Testa o arquivo narrative_new.json
"""

import os
import sys
import json
from typing import Dict, List, Any

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def carregar_narrative_new():
    """Carrega o arquivo narrative_new.json"""
    caminho = os.path.join(os.path.dirname(__file__), '..', 'data', 'narrative_new.json')
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {caminho}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar JSON: {e}")
        return None
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo: {e}")
        return None

def validar_estrutura_cena(cena: Dict, cena_id: str) -> List[str]:
    """Valida a estrutura de uma cena"""
    erros = []
    
    # Verificar campos obrigatórios
    if "id" not in cena:
        erros.append(f"Cena sem 'id'")
    
    # Verificar startTrigger
    if "startTrigger" in cena:
        trigger = cena["startTrigger"]
        if "type" not in trigger:
            erros.append(f"Cena {cena_id}: startTrigger sem 'type'")
        else:
            trigger_type = trigger["type"]
            params = trigger.get("params", {})
            
            # Validar parâmetros baseado no tipo
            if trigger_type == "enter_location":
                if "locationId" not in params:
                    erros.append(f"Cena {cena_id}: startTrigger 'enter_location' sem 'locationId'")
            elif trigger_type == "race_finished":
                if "raceId" not in params:
                    erros.append(f"Cena {cena_id}: startTrigger 'race_finished' sem 'raceId'")
            elif trigger_type == "time_passed":
                if "days" not in params and "daysSinceScene" not in params and "daysSinceChapterStart" not in params:
                    erros.append(f"Cena {cena_id}: startTrigger 'time_passed' sem parâmetro de tempo")
            elif trigger_type == "reputation_threshold":
                if "minReputation" not in params:
                    erros.append(f"Cena {cena_id}: startTrigger 'reputation_threshold' sem 'minReputation'")
            elif trigger_type == "race_selected":
                if "raceId" not in params:
                    erros.append(f"Cena {cena_id}: startTrigger 'race_selected' sem 'raceId'")
    
    # Verificar linhas
    if "lines" in cena:
        for i, line in enumerate(cena["lines"]):
            if "speaker" not in line and "type" not in line:
                erros.append(f"Cena {cena_id}, linha {i}: sem 'speaker' ou 'type'")
            if "text" not in line and "type" not in line:
                erros.append(f"Cena {cena_id}, linha {i}: sem 'text' ou 'type'")
    
    # Verificar choices
    if "choices" in cena:
        for i, choice in enumerate(cena["choices"]):
            if "id" not in choice:
                erros.append(f"Cena {cena_id}, escolha {i}: sem 'id'")
            if "text" not in choice:
                erros.append(f"Cena {cena_id}, escolha {i}: sem 'text'")
    
    # Verificar effects
    if "effects" in cena:
        for effect in cena["effects"]:
            # Validar formato básico dos efeitos
            if not isinstance(effect, str):
                erros.append(f"Cena {cena_id}: efeito não é string: {effect}")
    
    return erros

def validar_estrutura_capitulo(capitulo: Dict) -> List[str]:
    """Valida a estrutura de um capítulo"""
    erros = []
    
    if "id" not in capitulo:
        erros.append("Capítulo sem 'id'")
    if "name" not in capitulo:
        erros.append(f"Capítulo {capitulo.get('id', '?')}: sem 'name'")
    if "scenes" not in capitulo:
        erros.append(f"Capítulo {capitulo.get('id', '?')}: sem 'scenes'")
    else:
        scenes = capitulo["scenes"]
        if not isinstance(scenes, list):
            erros.append(f"Capítulo {capitulo.get('id', '?')}: 'scenes' não é uma lista")
        else:
            for scene in scenes:
                scene_id = scene.get("id", "?")
                erros.extend(validar_estrutura_cena(scene, scene_id))
    
    return erros

def testar_gatilhos(data: Dict):
    """Testa os gatilhos definidos nas cenas"""
    print("\n" + "="*60)
    print("TESTANDO GATILHOS")
    print("="*60)
    
    tipos_gatilhos = {}
    cenas_por_gatilho = {}
    
    for chapter in data.get("chapters", []):
        chapter_id = chapter.get("id", "?")
        for scene in chapter.get("scenes", []):
            scene_id = scene.get("id", "?")
            start_trigger = scene.get("startTrigger")
            
            if start_trigger:
                trigger_type = start_trigger.get("type", "?")
                tipos_gatilhos[trigger_type] = tipos_gatilhos.get(trigger_type, 0) + 1
                
                if trigger_type not in cenas_por_gatilho:
                    cenas_por_gatilho[trigger_type] = []
                cenas_por_gatilho[trigger_type].append(f"{chapter_id}/{scene_id}")
            else:
                tipos_gatilhos["immediate (implícito)"] = tipos_gatilhos.get("immediate (implícito)", 0) + 1
    
    print("\n📊 Estatísticas de Gatilhos:")
    for tipo, count in sorted(tipos_gatilhos.items()):
        print(f"  {tipo}: {count} cena(s)")
    
    print("\n📋 Cenas por Tipo de Gatilho:")
    for tipo, cenas in sorted(cenas_por_gatilho.items()):
        print(f"\n  {tipo}:")
        for cena in cenas[:5]:  # Mostrar apenas as primeiras 5
            print(f"    - {cena}")
        if len(cenas) > 5:
            print(f"    ... e mais {len(cenas) - 5} cena(s)")

def testar_efeitos(data: Dict):
    """Testa os efeitos definidos nas cenas"""
    print("\n" + "="*60)
    print("TESTANDO EFEITOS")
    print("="*60)
    
    efeitos_contagem = {}
    efeitos_por_cena = {}
    
    for chapter in data.get("chapters", []):
        chapter_id = chapter.get("id", "?")
        for scene in chapter.get("scenes", []):
            scene_id = scene.get("id", "?")
            effects = scene.get("effects", [])
            
            for effect in effects:
                # Extrair o tipo do efeito (antes do :)
                if ":" in effect:
                    effect_type = effect.split(":")[0]
                else:
                    effect_type = effect
                
                efeitos_contagem[effect_type] = efeitos_contagem.get(effect_type, 0) + 1
                
                if effect_type not in efeitos_por_cena:
                    efeitos_por_cena[effect_type] = []
                efeitos_por_cena[effect_type].append(f"{chapter_id}/{scene_id}")
    
    print("\n📊 Estatísticas de Efeitos:")
    for efeito, count in sorted(efeitos_contagem.items()):
        print(f"  {efeito}: {count} ocorrência(s)")
    
    # Verificar efeitos críticos
    efeitos_criticos = ["autoSave", "unlockLocation", "unlockRace", "endChapter", "startChapter"]
    print("\n✅ Verificação de Efeitos Críticos:")
    for efeito in efeitos_criticos:
        if efeito in efeitos_contagem:
            print(f"  ✓ {efeito}: {efeitos_contagem[efeito]} ocorrência(s)")
        else:
            print(f"  ⚠ {efeito}: não encontrado")

def testar_condicoes(data: Dict):
    """Testa as condições definidas nas cenas"""
    print("\n" + "="*60)
    print("TESTANDO CONDIÇÕES")
    print("="*60)
    
    condicoes_encontradas = set()
    cenas_com_condicoes = []
    
    for chapter in data.get("chapters", []):
        chapter_id = chapter.get("id", "?")
        for scene in chapter.get("scenes", []):
            scene_id = scene.get("id", "?")
            
            # Verificar condições em startTrigger
            start_trigger = scene.get("startTrigger")
            if start_trigger and "conditions" in start_trigger:
                conds = start_trigger["conditions"]
                for cond in conds:
                    condicoes_encontradas.add(cond)
                cenas_com_condicoes.append(f"{chapter_id}/{scene_id}")
            
            # Verificar condições em lines
            for line in scene.get("lines", []):
                if "conditions" in line:
                    conds = line.get("conditions", [])
                    for cond in conds:
                        condicoes_encontradas.add(cond)
                    cenas_com_condicoes.append(f"{chapter_id}/{scene_id}")
            
            # Verificar condições em choices
            for choice in scene.get("choices", []):
                if "conditions" in choice:
                    conds = choice.get("conditions", [])
                    for cond in conds:
                        condicoes_encontradas.add(cond)
                    cenas_com_condicoes.append(f"{chapter_id}/{scene_id}")
    
    print(f"\n📊 Total de condições únicas encontradas: {len(condicoes_encontradas)}")
    print("\n📋 Condições encontradas:")
    for cond in sorted(condicoes_encontradas):
        print(f"  - {cond}")
    
    print(f"\n📊 Cenas com condições: {len(set(cenas_com_condicoes))}")

def testar_referencias_cenas(data: Dict):
    """Testa se todas as referências de cenas (nextSceneId) são válidas"""
    print("\n" + "="*60)
    print("TESTANDO REFERÊNCIAS DE CENAS")
    print("="*60)
    
    # Coletar todos os IDs de cenas
    todas_cenas = {}
    for chapter in data.get("chapters", []):
        chapter_id = chapter.get("id", "?")
        for scene in chapter.get("scenes", []):
            scene_id = scene.get("id", "?")
            todas_cenas[scene_id] = f"{chapter_id}/{scene_id}"
    
    # Verificar referências
    referencias_invalidas = []
    referencias_validas = []
    
    for chapter in data.get("chapters", []):
        chapter_id = chapter.get("id", "?")
        for scene in chapter.get("scenes", []):
            scene_id = scene.get("id", "?")
            
            # Verificar nextSceneId
            next_scene = scene.get("nextSceneId")
            if next_scene:
                if next_scene in todas_cenas:
                    referencias_validas.append(f"{chapter_id}/{scene_id} -> {next_scene}")
                else:
                    referencias_invalidas.append(f"{chapter_id}/{scene_id} -> {next_scene} (NÃO ENCONTRADA)")
            
            # Verificar nextSceneId em choices
            for choice in scene.get("choices", []):
                next_scene = choice.get("nextSceneId")
                if next_scene:
                    if next_scene in todas_cenas:
                        referencias_validas.append(f"{chapter_id}/{scene_id} (choice) -> {next_scene}")
                    else:
                        referencias_invalidas.append(f"{chapter_id}/{scene_id} (choice) -> {next_scene} (NÃO ENCONTRADA)")
    
    print(f"\n✅ Referências válidas: {len(referencias_validas)}")
    print(f"❌ Referências inválidas: {len(referencias_invalidas)}")
    
    if referencias_invalidas:
        print("\n⚠️  Referências inválidas encontradas:")
        for ref in referencias_invalidas[:10]:  # Mostrar apenas as primeiras 10
            print(f"  - {ref}")
        if len(referencias_invalidas) > 10:
            print(f"  ... e mais {len(referencias_invalidas) - 10} referência(s) inválida(s)")

def testar_pausas_narrativas(data: Dict):
    """Testa se as pausas narrativas (nextSceneId: null) estão bem posicionadas"""
    print("\n" + "="*60)
    print("TESTANDO PAUSAS NARRATIVAS")
    print("="*60)
    
    cenas_com_pausa = []
    cenas_sem_pausa = []
    
    for chapter in data.get("chapters", []):
        chapter_id = chapter.get("id", "?")
        for scene in chapter.get("scenes", []):
            scene_id = scene.get("id", "?")
            next_scene = scene.get("nextSceneId")
            
            if next_scene is None:
                cenas_com_pausa.append(f"{chapter_id}/{scene_id}")
            else:
                cenas_sem_pausa.append(f"{chapter_id}/{scene_id}")
    
    print(f"\n📊 Cenas com pausa (nextSceneId: null): {len(cenas_com_pausa)}")
    print(f"📊 Cenas sem pausa (com nextSceneId): {len(cenas_sem_pausa)}")
    
    # Verificar se cenas com pausa têm autoSave
    cenas_com_pausa_e_autosave = []
    cenas_com_pausa_sem_autosave = []
    
    for chapter in data.get("chapters", []):
        chapter_id = chapter.get("id", "?")
        for scene in chapter.get("scenes", []):
            scene_id = scene.get("id", "?")
            if scene.get("nextSceneId") is None:
                effects = scene.get("effects", [])
                if "autoSave" in effects:
                    cenas_com_pausa_e_autosave.append(f"{chapter_id}/{scene_id}")
                else:
                    cenas_com_pausa_sem_autosave.append(f"{chapter_id}/{scene_id}")
    
    print(f"\n✅ Cenas com pausa E autoSave: {len(cenas_com_pausa_e_autosave)}")
    print(f"⚠️  Cenas com pausa SEM autoSave: {len(cenas_com_pausa_sem_autosave)}")
    
    if cenas_com_pausa_sem_autosave:
        print("\n⚠️  Cenas com pausa que podem precisar de autoSave:")
        for cena in cenas_com_pausa_sem_autosave[:10]:
            print(f"  - {cena}")
        if len(cenas_com_pausa_sem_autosave) > 10:
            print(f"  ... e mais {len(cenas_com_pausa_sem_autosave) - 10} cena(s)")

def main():
    """Função principal de teste"""
    print("="*60)
    print("TESTE DO NOVO SISTEMA NARRATIVO")
    print("Arquivo: narrative_new.json")
    print("="*60)
    
    # Carregar arquivo
    data = carregar_narrative_new()
    if not data:
        print("\n❌ Não foi possível carregar o arquivo. Abortando testes.")
        return 1
    
    print("\n✅ Arquivo carregado com sucesso!")
    
    # Validar estrutura básica
    print("\n" + "="*60)
    print("VALIDANDO ESTRUTURA")
    print("="*60)
    
    erros = []
    if "chapters" not in data:
        erros.append("Arquivo sem 'chapters'")
    else:
        for chapter in data["chapters"]:
            erros.extend(validar_estrutura_capitulo(chapter))
    
    if erros:
        print(f"\n❌ {len(erros)} erro(s) encontrado(s):")
        for erro in erros[:20]:  # Mostrar apenas os primeiros 20
            print(f"  - {erro}")
        if len(erros) > 20:
            print(f"  ... e mais {len(erros) - 20} erro(s)")
    else:
        print("\n✅ Estrutura válida!")
    
    # Estatísticas gerais
    print("\n" + "="*60)
    print("ESTATÍSTICAS GERAIS")
    print("="*60)
    
    total_capitulos = len(data.get("chapters", []))
    total_cenas = sum(len(ch.get("scenes", [])) for ch in data.get("chapters", []))
    total_choices = sum(len(sc.get("choices", [])) for ch in data.get("chapters", []) for sc in ch.get("scenes", []))
    
    print(f"\n📊 Total de capítulos: {total_capitulos}")
    print(f"📊 Total de cenas: {total_cenas}")
    print(f"📊 Total de escolhas: {total_choices}")
    
    # Executar testes específicos
    testar_gatilhos(data)
    testar_efeitos(data)
    testar_condicoes(data)
    testar_referencias_cenas(data)
    testar_pausas_narrativas(data)
    
    print("\n" + "="*60)
    print("TESTE CONCLUÍDO")
    print("="*60)
    
    return 0 if not erros else 1

if __name__ == "__main__":
    sys.exit(main())

