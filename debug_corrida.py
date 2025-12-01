#!/usr/bin/env python3
"""
Script de debug para investigar por que as estatísticas não estão sendo registradas após a corrida
"""

import os
import sys
import json

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_estatisticas():
    """Verifica o estado das estatísticas"""
    print("=" * 80)
    print("DEBUG: Verificando Estatísticas")
    print("=" * 80)
    
    try:
        from core.estatisticas import gerenciador_estatisticas
        
        # Obter estatísticas gerais
        stats = gerenciador_estatisticas.obter_estatisticas_gerais()
        print(f"\n[ESTATÍSTICAS GERAIS]")
        print(f"  corridas_completas: {stats.get('corridas_completas', 0)}")
        print(f"  total_corridas: {stats.get('total_corridas', 0)}")
        print(f"  vitorias: {stats.get('vitorias', 0)}")
        print(f"  Stats completo: {json.dumps(stats, indent=2, default=str)}")
        
        # Verificar estatísticas da pista 1
        print(f"\n[ESTATÍSTICAS PISTA 1]")
        stats_pista = gerenciador_estatisticas._obter_estatisticas_pista(1)
        print(f"  melhor_tempo: {stats_pista.get('melhor_tempo', None)}")
        print(f"  melhor_posicao: {stats_pista.get('melhor_posicao', None)}")
        print(f"  total_corridas: {stats_pista.get('total_corridas', 0)}")
        print(f"  Stats pista completo: {json.dumps(stats_pista, indent=2, default=str)}")
        
        # Verificar arquivo de estatísticas
        from config import DIR_PROJETO
        caminho_stats = os.path.join(DIR_PROJETO, 'data', 'estatisticas.json')
        print(f"\n[ARQUIVO DE ESTATÍSTICAS]")
        print(f"  Caminho: {caminho_stats}")
        print(f"  Existe: {os.path.exists(caminho_stats)}")
        
        if os.path.exists(caminho_stats):
            with open(caminho_stats, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"  Conteúdo: {json.dumps(data, indent=2, default=str)}")
        
    except Exception as e:
        print(f"\n[ERRO] Ao verificar estatísticas: {e}")
        import traceback
        traceback.print_exc()

def debug_progresso():
    """Verifica o estado do progresso"""
    print("\n" + "=" * 80)
    print("DEBUG: Verificando Progresso")
    print("=" * 80)
    
    try:
        from core.progresso import gerenciador_progresso
        
        print(f"\n[PROGRESSO]")
        print(f"  ultima_corrida_campanha: {getattr(gerenciador_progresso, 'ultima_corrida_campanha', None)}")
        print(f"  carro_p1_atual: {gerenciador_progresso.carro_p1_atual}")
        
        # Verificar arquivo de progresso
        from config import DIR_PROJETO
        caminho_progresso = os.path.join(DIR_PROJETO, 'data', 'progresso.json')
        print(f"\n[ARQUIVO DE PROGRESSO]")
        print(f"  Caminho: {caminho_progresso}")
        print(f"  Existe: {os.path.exists(caminho_progresso)}")
        
        if os.path.exists(caminho_progresso):
            with open(caminho_progresso, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"  Conteúdo: {json.dumps(data, indent=2, default=str)}")
        
    except Exception as e:
        print(f"\n[ERRO] Ao verificar progresso: {e}")
        import traceback
        traceback.print_exc()

def debug_missao():
    """Verifica o estado da missão"""
    print("\n" + "=" * 80)
    print("DEBUG: Verificando Missão")
    print("=" * 80)
    
    try:
        from core.missoes import gerenciador_missoes
        
        print(f"\n[MISSÃO BATISMO DE PISTA]")
        missao = gerenciador_missoes.missoes.get("m6_batismo_de_pista")
        if missao:
            print(f"  Nome: {missao.get('nome')}")
            print(f"  Objetivo: {missao.get('objetivo')}")
            print(f"  Ativa: {gerenciador_missoes.missao_ativa_id == 'm6_batismo_de_pista'}")
            print(f"  Completa: {gerenciador_missoes.esta_completa('m6_batismo_de_pista')}")
        else:
            print("  Missão não encontrada!")
        
        print(f"\n[MISSÃO ATIVA]")
        missao_ativa = gerenciador_missoes.obter_missao_ativa()
        if missao_ativa:
            print(f"  ID: {missao_ativa.get('id')}")
            print(f"  Nome: {missao_ativa.get('nome')}")
        else:
            print("  Nenhuma missão ativa")
        
    except Exception as e:
        print(f"\n[ERRO] Ao verificar missão: {e}")
        import traceback
        traceback.print_exc()

def debug_narrativa():
    """Verifica o estado da narrativa"""
    print("\n" + "=" * 80)
    print("DEBUG: Verificando Narrativa")
    print("=" * 80)
    
    try:
        from core.narrative_system import narrative_system
        
        print(f"\n[NARRATIVA]")
        print(f"  active: {narrative_system.active}")
        print(f"  current_scene_id: {narrative_system.current_scene_id}")
        print(f"  current_line_index: {narrative_system.current_line_index}")
        print(f"  lastRaceResult: {narrative_system.variables.get('lastRaceResult', None)}")
        
    except Exception as e:
        print(f"\n[ERRO] Ao verificar narrativa: {e}")
        import traceback
        traceback.print_exc()

def simular_registro_corrida():
    """Simula o registro de uma corrida para testar"""
    print("\n" + "=" * 80)
    print("DEBUG: Simulando Registro de Corrida")
    print("=" * 80)
    
    try:
        from core.estatisticas import gerenciador_estatisticas
        
        print("\n[ANTES]")
        stats_antes = gerenciador_estatisticas.obter_estatisticas_gerais()
        print(f"  corridas_completas: {stats_antes.get('corridas_completas', 0)}")
        
        stats_pista_antes = gerenciador_estatisticas._obter_estatisticas_pista(1)
        print(f"  melhor_tempo: {stats_pista_antes.get('melhor_tempo', None)}")
        print(f"  melhor_posicao: {stats_pista_antes.get('melhor_posicao', None)}")
        
        # Simular registro
        print("\n[REGISTRANDO] Corrida na pista 1, posição 1, tempo 31.99s")
        gerenciador_estatisticas.registrar_corrida_completa(1, 1, 31.99)
        
        print("\n[DEPOIS]")
        stats_depois = gerenciador_estatisticas.obter_estatisticas_gerais()
        print(f"  corridas_completas: {stats_depois.get('corridas_completas', 0)}")
        
        stats_pista_depois = gerenciador_estatisticas._obter_estatisticas_pista(1)
        print(f"  melhor_tempo: {stats_pista_depois.get('melhor_tempo', None)}")
        print(f"  melhor_posicao: {stats_pista_depois.get('melhor_posicao', None)}")
        
        # Salvar
        print("\n[SALVANDO]")
        gerenciador_estatisticas.salvar()
        print("  Estatísticas salvas!")
        
    except Exception as e:
        print(f"\n[ERRO] Ao simular registro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("SCRIPT DE DEBUG - CORRIDA TRAINING_01")
    print("=" * 80)
    
    # Executar todos os debugs
    debug_estatisticas()
    debug_progresso()
    debug_missao()
    debug_narrativa()
    
    # Perguntar se quer simular
    print("\n" + "=" * 80)
    resposta = input("Deseja simular o registro de uma corrida? (s/n): ")
    if resposta.lower() == 's':
        simular_registro_corrida()
        print("\n" + "=" * 80)
        print("Verificando novamente após simulação...")
        print("=" * 80)
        debug_estatisticas()
    
    print("\n" + "=" * 80)
    print("DEBUG CONCLUÍDO")
    print("=" * 80)

