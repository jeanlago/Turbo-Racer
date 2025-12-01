# debug_roteiro.py
"""
Script de debug para verificar o fluxo completo do roteiro no modo campanha
"""
import os
import sys
import json

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame

# Inicializar pygame para carregar módulos que dependem dele
pygame.init()

from config import DIR_PROJETO
from core.progresso import gerenciador_progresso
from core.estatisticas import gerenciador_estatisticas
from core.missoes import gerenciador_missoes
from core.narrative_system import narrative_system
from core.boris import boris

def print_separador(titulo=""):
    """Imprime um separador visual"""
    print("\n" + "="*80)
    if titulo:
        print(f"  {titulo}")
        print("="*80 + "\n")
    else:
        print("="*80 + "\n")

def print_debug_progresso():
    """Imprime informações sobre o progresso"""
    print_separador("DEBUG: PROGRESSO")
    
    print(f"[PROGRESSO]")
    print(f"  Capitulo atual: {gerenciador_progresso.obter_capitulo_atual()}")
    print(f"  Boris primeira aparição: {gerenciador_progresso.boris_primeira_aparicao_mostrada}")
    print(f"  Boris nome revelado: {gerenciador_progresso.boris_nome_revelado}")
    print(f"  Pixel primeira aparição: {gerenciador_progresso.pixel_primeira_aparicao_mostrada}")
    print(f"  Pixel nome revelado: {gerenciador_progresso.pixel_nome_revelado}")
    print(f"  Crank tutorial mostrado: {gerenciador_progresso.crank_tutorial_mostrado}")
    print(f"  Ultima corrida campanha: {getattr(gerenciador_progresso, 'ultima_corrida_campanha', None)}")
    
    # Verificar arquivo de progresso
    caminho_progresso = os.path.join(DIR_PROJETO, "data", "progresso.json")
    print(f"\n[ARQUIVO DE PROGRESSO]")
    print(f"  Caminho: {caminho_progresso}")
    print(f"  Existe: {os.path.exists(caminho_progresso)}")
    
    if os.path.exists(caminho_progresso):
        try:
            with open(caminho_progresso, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"  Boris primeira aparição (arquivo): {data.get('boris_primeira_aparicao_mostrada', False)}")
                print(f"  Boris nome revelado (arquivo): {data.get('boris_nome_revelado', False)}")
                print(f"  Pixel primeira aparição (arquivo): {data.get('pixel_primeira_aparicao_mostrada', False)}")
                print(f"  Pixel nome revelado (arquivo): {data.get('pixel_nome_revelado', False)}")
                print(f"  Ultima corrida campanha (arquivo): {data.get('ultima_corrida_campanha', None)}")
        except Exception as e:
            print(f"  Erro ao ler arquivo: {e}")

def print_debug_missoes():
    """Imprime informações sobre as missões"""
    print_separador("DEBUG: MISSÕES")
    
    print(f"[MISSÕES]")
    print(f"  Missão ativa: {gerenciador_missoes.missao_ativa_id}")
    
    # Listar todas as missões do capítulo 1
    print(f"\n[MISSÕES CAPÍTULO 1]")
    for missao_id, missao in gerenciador_missoes.missoes.items():
        if missao.get("chapter") == "ch1":
            completa = gerenciador_missoes.esta_completa(missao_id)
            ativa = gerenciador_missoes.missao_ativa_id == missao_id
            print(f"  {missao_id}:")
            print(f"    Nome: {missao.get('nome', 'N/A')}")
            print(f"    Objetivo: {missao.get('objetivo', 'N/A')}")
            print(f"    Ativa: {ativa}")
            print(f"    Completa: {completa}")
            print(f"    Ativa em: {missao.get('activateOnSceneId', 'N/A')}")
            print(f"    Completa em: {missao.get('completeOnSceneId', 'N/A')}")
            print()

def print_debug_narrativa():
    """Imprime informações sobre a narrativa"""
    print_separador("DEBUG: NARRATIVA")
    
    print(f"[NARRATIVA]")
    print(f"  Active: {narrative_system.active}")
    print(f"  Current chapter: {narrative_system.current_chapter_id}")
    print(f"  Current scene: {narrative_system.current_scene_id}")
    print(f"  Current line index: {narrative_system.current_line_index}")
    print(f"  Flags: {narrative_system.flags}")
    print(f"  Variables: {narrative_system.variables}")
    
    # Verificar cenas do capítulo 1
    if narrative_system.narrative_data:
        print(f"\n[CENAS CAPÍTULO 1]")
        for chapter in narrative_system.narrative_data.get("chapters", []):
            if chapter.get("id") == "ch1":
                scenes = chapter.get("scenes", [])
                print(f"  Total de cenas: {len(scenes)}")
                for scene in scenes:
                    scene_id = scene.get("id")
                    is_current = scene_id == narrative_system.current_scene_id
                    print(f"    {scene_id}: {'<-- ATUAL' if is_current else ''}")
                    if scene.get("gameplayTrigger"):
                        trigger = scene.get("gameplayTrigger")
                        print(f"      Trigger: {trigger.get('trigger')}")
                    if scene.get("nextSceneId"):
                        print(f"      Próxima cena: {scene.get('nextSceneId')}")
                break

def print_debug_boris():
    """Imprime informações sobre o Boris"""
    print_separador("DEBUG: BORIS")
    
    print(f"[BORIS]")
    print(f"  Primeira aparição mostrada: {boris.primeira_aparicao_mostrada}")
    print(f"  Nome revelado: {boris.nome_revelado}")
    print(f"  Ativo: {boris.ativo}")
    print(f"  Fase diálogo: {boris.fase_dialogo}")
    print(f"  Loja aberta: {boris.loja_aberta}")

def print_debug_estatisticas():
    """Imprime informações sobre as estatísticas"""
    print_separador("DEBUG: ESTATÍSTICAS")
    
    stats = gerenciador_estatisticas.obter_estatisticas_gerais()
    print(f"[ESTATÍSTICAS GERAIS]")
    print(f"  Corridas completas: {stats.get('corridas_completas', 0)}")
    
    stats_pista = gerenciador_estatisticas._obter_estatisticas_pista(1)
    if stats_pista:
        print(f"\n[ESTATÍSTICAS PISTA 1]")
        print(f"  Melhor tempo: {stats_pista.get('melhor_tempo', None)}")
        print(f"  Melhor posição: {stats_pista.get('melhor_posicao', None)}")
        print(f"  Corridas completas: {stats_pista.get('corridas_completas', 0)}")

def verificar_fluxo_roteiro():
    """Verifica o fluxo completo do roteiro"""
    print_separador("VERIFICAÇÃO DO FLUXO DO ROTEIRO")
    
    # Verificar sequência esperada
    sequencia_esperada = [
        ("ch1_0_prologue", "Prólogo"),
        ("ch1_1_crank_garage_intro", "Introdução do Crank"),
        ("ch1_3_meet_boris", "Encontrar Boris"),
        ("ch1_4_return_garage_upgrade", "Voltar à garagem e instalar upgrade"),
        ("ch1_5_first_race_unlocked", "Corrida desbloqueada"),
        ("ch1_6_post_first_race_and_pixel", "Pós-corrida e Pixel"),
        ("ch1_7_pixel_intro", "Introdução do Pixel"),
    ]
    
    print("[SEQUÊNCIA ESPERADA]")
    for scene_id, descricao in sequencia_esperada:
        # Verificar se a cena foi vista/completada
        foi_vista = False
        if scene_id == "ch1_3_meet_boris":
            foi_vista = gerenciador_progresso.boris_primeira_aparicao_mostrada
        elif scene_id == "ch1_7_pixel_intro":
            foi_vista = gerenciador_progresso.pixel_primeira_aparicao_mostrada
        elif scene_id == "ch1_1_crank_garage_intro":
            foi_vista = gerenciador_progresso.crank_tutorial_mostrado
        
        status = "✓ VISTA" if foi_vista else "✗ NÃO VISTA"
        print(f"  {scene_id} ({descricao}): {status}")

def main_debug():
    """Função principal de debug"""
    print_separador("SCRIPT DE DEBUG - FLUXO DO ROTEIRO")
    
    # Forçar recarregamento
    gerenciador_progresso.carregar()
    gerenciador_estatisticas.carregar()
    gerenciador_missoes.carregar()
    boris.carregar_estado()
    
    # Imprimir informações
    print_debug_progresso()
    print_debug_missoes()
    print_debug_narrativa()
    print_debug_boris()
    print_debug_estatisticas()
    verificar_fluxo_roteiro()
    
    print_separador("DEBUG CONCLUÍDO")
    
    # Perguntar se quer simular algo
    print("\nOpções:")
    print("1. Simular primeira aparição do Boris como vista")
    print("2. Simular primeira aparição do Pixel como vista")
    print("3. Verificar trigger da cena ch1_3_meet_boris")
    print("4. Sair")
    
    opcao = input("\nEscolha uma opção (1-4): ").strip()
    
    if opcao == "1":
        print("\n[SIMULANDO] Marcando primeira aparição do Boris como vista...")
        gerenciador_progresso.boris_primeira_aparicao_mostrada = True
        gerenciador_progresso.boris_nome_revelado = True
        gerenciador_progresso.salvar()
        boris.primeira_aparicao_mostrada = True
        boris.nome_revelado = True
        print("✓ Feito!")
    elif opcao == "2":
        print("\n[SIMULANDO] Marcando primeira aparição do Pixel como vista...")
        gerenciador_progresso.pixel_primeira_aparicao_mostrada = True
        gerenciador_progresso.pixel_nome_revelado = True
        gerenciador_progresso.salvar()
        print("✓ Feito!")
    elif opcao == "3":
        print("\n[VERIFICANDO] Trigger da cena ch1_3_meet_boris...")
        if narrative_system.narrative_data:
            for chapter in narrative_system.narrative_data.get("chapters", []):
                if chapter.get("id") == "ch1":
                    for scene in chapter.get("scenes", []):
                        if scene.get("id") == "ch1_3_meet_boris":
                            trigger = scene.get("gameplayTrigger")
                            if trigger:
                                print(f"  Trigger encontrado: {trigger.get('trigger')}")
                                print(f"  Parâmetros: {trigger.get('params', {})}")
                            else:
                                print("  Nenhum trigger encontrado")
                            next_scene = scene.get("nextSceneId")
                            if next_scene:
                                print(f"  Próxima cena: {next_scene}")
                            break
                    break

if __name__ == "__main__":
    main_debug()

